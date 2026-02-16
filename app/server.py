#!/usr/bin/env python3
"""
Face Attendance Backend Server - Complete Version
รวม API, WebSocket, SQLite และ Telegram Notification
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from pathlib import Path
import asyncio
import sqlite3
import json
import os
import sys
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================
# Database Setup
# ============================================================
DB_PATH = Path(__file__).parent.parent / "database" / "attendance.db"

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db()
    c = conn.cursor()
    
    # Students table
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            department TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    # Attendance sessions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_name TEXT,
            course_id TEXT,
            started_at TEXT NOT NULL,
            ended_at TEXT,
            status TEXT DEFAULT 'active',
            total_checked_in INTEGER DEFAULT 0
        )
    ''')
    
    # Activity logs table for tracking user actions
    c.execute('''
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_type TEXT NOT NULL,
            description TEXT NOT NULL,
            user_ip TEXT,
            user_agent TEXT,
            target_table TEXT,
            target_id INTEGER,
            old_data TEXT,
            new_data TEXT,
            timestamp TEXT NOT NULL,
            success BOOLEAN DEFAULT TRUE
        )
    ''')
    
    
    # Check if attendance table exists and has the right columns
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='attendance'")
    table_exists = c.fetchone() is not None
    
    if table_exists:
        # Check columns
        c.execute("PRAGMA table_info(attendance)")
        columns = [col[1] for col in c.fetchall()]
        
        # Add missing columns if needed
        if 'name' not in columns:
            try:
                c.execute('ALTER TABLE attendance ADD COLUMN name TEXT')
            except:
                pass
        if 'confidence_score' not in columns:
            try:
                c.execute('ALTER TABLE attendance ADD COLUMN confidence_score REAL')
            except:
                pass
        if 'camera_id' not in columns:
            try:
                c.execute('ALTER TABLE attendance ADD COLUMN camera_id TEXT')
            except:
                pass
        if 'image_base64' not in columns:
            try:
                c.execute('ALTER TABLE attendance ADD COLUMN image_base64 TEXT')
            except:
                pass
        if 'modified_at' not in columns:
            try:
                c.execute('ALTER TABLE attendance ADD COLUMN modified_at TEXT')
            except:
                pass
    else:
        # Create new attendance table
        c.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                student_id INTEGER,
                name TEXT,
                timestamp TEXT NOT NULL,
                confidence_score REAL,
                camera_id TEXT,
                image_base64 TEXT,
                modified_at TEXT,
                FOREIGN KEY (session_id) REFERENCES attendance_sessions (id),
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        ''')
    
    # Create indexes (ignore errors if they exist)
    try:
        c.execute('CREATE INDEX IF NOT EXISTS idx_attendance_timestamp ON attendance(timestamp)')
    except:
        pass
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized: {DB_PATH}")

# ============================================================
# WebSocket Manager
# ============================================================
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        print(f"📡 WebSocket connected. Total: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        print(f"📡 WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        async with self._lock:
            connections = list(self.active_connections)
        
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception:
                await self.disconnect(connection)

manager = ConnectionManager()

# ============================================================
# Telegram Notification System
# ============================================================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def send_telegram_message(message: str, parse_mode: str = "HTML"):
    """Send notification to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram not configured (set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env)")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": parse_mode
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, timeout=10)
            if response.status_code == 200:
                print(f"📱 Telegram sent: {message[:50]}...")
                return True
            else:
                print(f"❌ Telegram failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False

async def send_telegram_photo(photo_base64: str, caption: str = ""):
    """Send photo to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    
    try:
        import base64
        photo_bytes = base64.b64decode(photo_base64)
        
        async with httpx.AsyncClient() as client:
            files = {"photo": ("attendance.jpg", photo_bytes, "image/jpeg")}
            data = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption}
            response = await client.post(url, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                print(f"📷 Telegram photo sent")
                return True
            else:
                print(f"❌ Telegram photo failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Telegram photo error: {e}")
        return False

# ============================================================
# Activity Logging System
# ============================================================
async def log_activity(
    action_type: str,
    description: str,
    request: Request = None,
    target_table: str = None,
    target_id: int = None,
    old_data: Dict = None,
    new_data: Dict = None,
    success: bool = True
):
    """Log user activity to database and optionally send to Telegram"""
    try:
        conn = get_db()
        c = conn.cursor()
        
        # Get user info from request (with error handling)
        try:
            user_ip = request.client.host if request and hasattr(request, 'client') else "system"
            user_agent = request.headers.get("user-agent", "") if request and hasattr(request, 'headers') else "system"
        except Exception:
            user_ip = "system"
            user_agent = "system"
        
        # Insert log
        c.execute('''
            INSERT INTO activity_logs 
            (action_type, description, user_ip, user_agent, target_table, target_id, old_data, new_data, timestamp, success)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            action_type,
            description,
            user_ip,
            user_agent,
            target_table,
            target_id,
            json.dumps(old_data) if old_data else None,
            json.dumps(new_data) if new_data else None,
            datetime.now().isoformat(),
            success
        ))
        
        conn.commit()
        conn.close()
        
        # Send to Telegram if enabled and it's an important action
        if state.telegram_enabled and action_type in ['attendance_check', 'attendance_edit', 'attendance_delete', 'manual_attendance']:
            await send_activity_to_telegram(action_type, description, user_ip, success)
            
    except Exception as e:
        print(f"❌ Logging error: {e}")

async def send_activity_to_telegram(action_type: str, description: str, user_ip: str, success: bool):
    """Send activity log to Telegram"""
    try:
        now = datetime.now()
        time_str = now.strftime('%H:%M:%S')
        date_str = now.strftime('%d/%m/%Y')
        
        # Action type emojis
        action_emojis = {
            'attendance_check': '✅',
            'attendance_edit': '✏️',
            'attendance_delete': '🗑️',
            'manual_attendance': '✋'
        }
        
        emoji = action_emojis.get(action_type, '📝')
        status_emoji = '✅' if success else '❌'
        
        message = f"{emoji} <b>กิจกรรมระบบ</b>\n"
        message += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        message += f"📅 <b>วันที่:</b> {date_str}\n"
        message += f"⏰ <b>เวลา:</b> {time_str}\n"
        message += f"🌐 <b>IP:</b> {user_ip}\n"
        message += f"{status_emoji} <b>สถานะ:</b> {'สำเร็จ' if success else 'ล้มเหลว'}\n\n"
        message += f"📝 <b>รายละเอียด:</b>\n{description}"
        
        asyncio.create_task(send_telegram_message(message))
        
    except Exception as e:
        print(f"❌ Telegram activity log error: {e}")

# ============================================================
# Global State
# ============================================================
class AppState:
    def __init__(self):
        self.last_detection = None
        self.last_update = None
        self.recent_logs = []
        self.telegram_enabled = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)

state = AppState()

# ============================================================
# FastAPI App
# ============================================================
app = FastAPI(
    title="Face Attendance System",
    description="Backend API for face recognition attendance",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ============================================================
# Startup Event
# ============================================================
@app.on_event("startup")
async def startup():
    print("=" * 60)
    print("🚀 Face Attendance Backend Starting...")
    print("=" * 60)
    init_db()
    
    
    print(f"📍 API Docs: http://localhost:8000/docs")
    print(f"📍 Health: http://localhost:8000/health")
    print(f"📍 WebSocket: ws://localhost:8000/ws")
    print("=" * 60)

# ============================================================
# Basic Endpoints
# ============================================================
@app.get("/")
async def root():
    return {"message": "Face Attendance API", "version": "3.0.0", "docs": "/docs"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "3.0.0",
        "database": str(DB_PATH),
        "websocket_clients": len(manager.active_connections)
    }

# ============================================================
# WebSocket Endpoint
# ============================================================
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial state
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket connected successfully"
        })
        
        while True:
            # Keep connection alive, receive any messages
            data = await websocket.receive_text()
            # Echo back or handle commands
            await websocket.send_json({"type": "ack", "data": data})
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        await manager.disconnect(websocket)

# ============================================================
# Detection Ingest Endpoint
# ============================================================
@app.post("/api/v1/ingest")
async def ingest_detection(payload: Dict[str, Any]):
    """Receive face detection data and broadcast via WebSocket (real-time only)"""
    global state
    
    state.last_detection = payload
    state.last_update = datetime.now(timezone.utc).isoformat()
    
    # Broadcast to WebSocket clients for real-time updates (no database logging)
    await manager.broadcast({
        "type": "detection",
        "payload": payload
    })
    
    return {"status": "ok", "received": True}

# ============================================================
# Attendance Endpoints
# ============================================================
@app.post("/api/v1/attendance/check")
async def check_attendance(payload: Dict[str, Any] = None, request: Request = None):
    """Save detected faces as attendance
    
    รับ body จาก frontend: {known_faces, camera_id, stream_image}
    ถ้าไม่มี body จะใช้ state.last_detection แทน (backward compatible)
    """
    # ใช้ body ที่ส่งมา หรือ fallback ไปใช้ state.last_detection
    if payload and payload.get("known_faces"):
        data = payload
    elif state.last_detection:
        data = state.last_detection
    else:
        raise HTTPException(status_code=400, detail="No detection data available")
    
    known_faces = data.get("known_faces", [])
    
    if not known_faces:
        raise HTTPException(status_code=400, detail="No known faces detected")
    
    camera_id = data.get("camera_id", "unknown")
    stream_image = data.get("stream_image")
    
    conn = get_db()
    c = conn.cursor()
    
    saved_count = 0
    already_checked = []
    saved_names = []
    
    for face in known_faces:
        name = face.get("name", "Unknown")
        confidence = face.get("confidence", 0)
        
        # Check if already checked in the last 5 minutes (prevent spam)
        c.execute('''
            SELECT COUNT(*) FROM attendance 
            WHERE name = ? AND timestamp > datetime('now', '-5 minutes')
        ''', (name,))
        
        if c.fetchone()[0] > 0:
            already_checked.append(name)
            continue
        
        # Insert attendance record (allow multiple times per day)
        c.execute('''
            INSERT INTO attendance (name, timestamp, confidence_score, camera_id, image_base64)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            name,
            datetime.now().isoformat(),
            confidence,
            camera_id,
            stream_image
        ))
        
        saved_count += 1
        saved_names.append(name)
    
    conn.commit()
    
    # Log attendance check activity
    await log_activity(
        action_type="attendance_check",
        description=f"เช็คชื่อ {len(saved_names)} คน: {', '.join(saved_names)}" + 
                   (f" (เพิ่งเช็คแล้ว: {', '.join(already_checked)})" if already_checked else ""),
        request=request,
        target_table="attendance",
        new_data={"saved_names": saved_names, "already_checked": already_checked, "camera_id": camera_id},
        success=True
    )
    
    # Broadcast attendance update
    await manager.broadcast({
        "type": "attendance_checked",
        "saved": saved_names,
        "already_checked": already_checked
    })
    
    # Send Enhanced Telegram notification
    if saved_names and state.telegram_enabled:
        now = datetime.now()
        time_str = now.strftime('%H:%M:%S')
        date_str = now.strftime('%d/%m/%Y')
        thai_date = now.strftime('%d %B %Y')
        
        # Get comprehensive statistics (ใช้ conn ที่ยังเปิดอยู่)
        c2 = conn.cursor()
        
        # Total unique students today
        c2.execute('''
            SELECT COUNT(DISTINCT name) FROM attendance 
            WHERE DATE(timestamp) = DATE('now')
        ''')
        total_today = c2.fetchone()[0]
        
        # Total check-ins today (including multiple per person)
        c2.execute('''
            SELECT COUNT(*) FROM attendance 
            WHERE DATE(timestamp) = DATE('now')
        ''')
        total_checkins_today = c2.fetchone()[0]
        
        # Camera vs Manual breakdown
        c2.execute('''
            SELECT 
                SUM(CASE WHEN camera_id != 'manual' THEN 1 ELSE 0 END) as camera_count,
                SUM(CASE WHEN camera_id = 'manual' THEN 1 ELSE 0 END) as manual_count
            FROM attendance 
            WHERE DATE(timestamp) = DATE('now')
        ''')
        camera_manual = c2.fetchone()
        camera_count = camera_manual[0] or 0
        manual_count = camera_manual[1] or 0
        
        # Recent activity (last 30 minutes)
        c2.execute('''
            SELECT COUNT(DISTINCT name) FROM attendance 
            WHERE timestamp > datetime('now', '-30 minutes')
        ''')
        recent_activity = c2.fetchone()[0]
        
        # Build enhanced message
        tg_message = f"🎯 <b>การเช็คชื่อใหม่</b>\n"
        tg_message += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        tg_message += f"📅 <b>วันที่:</b> {thai_date}\n"
        tg_message += f"⏰ <b>เวลา:</b> {time_str}\n"
        tg_message += f"� <b>ประเภท:</b> {'📷 กล้อง' if camera_id != 'manual' else '✋ Manual'}\n\n"
        
        tg_message += f"✅ <b>เช็คชื่อครั้งนี้:</b> {len(saved_names)} คน\n"
        for i, name in enumerate(saved_names, 1):
            tg_message += f"   {i}. {name}\n"
        
        if already_checked:
            tg_message += f"\n⚠️ <b>เพิ่งเช็คแล้ว:</b> {len(already_checked)} คน\n"
            for name in already_checked:
                tg_message += f"   • {name}\n"
        
        tg_message += f"\n📊 <b>สถิติวันนี้:</b>\n"
        tg_message += f"👥 นักเรียนที่มา: {total_today} คน\n"
        tg_message += f"📝 ครั้งทั้งหมด: {total_checkins_today} ครั้ง\n"
        tg_message += f"📷 ด้วยกล้อง: {camera_count} ครั้ง\n"
        tg_message += f"✋ ด้วยมือ: {manual_count} ครั้ง\n"
        tg_message += f"🔥 ล่าสุด 30 นาที: {recent_activity} คน\n"
        
        # Send message
        asyncio.create_task(send_telegram_message(tg_message))
        
        # Send photo if available with enhanced caption
        if stream_image:
            caption = f"📷 เช็คชื่อ {time_str}\n👥 {', '.join(saved_names)}\n📊 รวมวันนี้: {total_today} คน"
            asyncio.create_task(send_telegram_photo(stream_image, caption))
    
    conn.close()
    
    return {
        "status": "success",
        "saved_count": saved_count,
        "saved_names": saved_names,
        "already_checked": already_checked
    }

@app.get("/api/v1/attendance/history")
async def get_attendance_history(
    limit: int = Query(100, ge=1, le=1000),
    date: Optional[str] = Query(None)
):
    """Get attendance history"""
    conn = get_db()
    c = conn.cursor()
    
    if date:
        c.execute('''
            SELECT * FROM attendance 
            WHERE DATE(timestamp) = ?
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (date, limit))
    else:
        c.execute('''
            SELECT * FROM attendance 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
    
    rows = c.fetchall()
    conn.close()
    
    history = [dict(row) for row in rows]
    
    return {
        "success": True,
        "count": len(history),
        "data": history
    }

@app.get("/api/v1/attendance/today")
async def get_today_attendance():
    """Get today's attendance"""
    conn = get_db()
    c = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    c.execute('''
        SELECT * FROM attendance 
        WHERE DATE(timestamp) = ?
        ORDER BY timestamp DESC
    ''', (today,))
    
    rows = c.fetchall()
    conn.close()
    
    return {
        "success": True,
        "date": today,
        "count": len(rows),
        "data": [dict(row) for row in rows]
    }

# ============================================================
# Students Endpoints
# ============================================================
@app.get("/api/v1/students")
async def get_students(
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None)
):
    """Get list of students with attendance count"""
    conn = get_db()
    c = conn.cursor()
    
    if search:
        c.execute('''
            SELECT s.*, COUNT(DISTINCT a.id) as attendance_count
            FROM students s
            LEFT JOIN attendance a ON s.name = a.name
            WHERE s.name LIKE ? OR s.student_id LIKE ?
            GROUP BY s.id
            ORDER BY s.created_at DESC 
            LIMIT ?
        ''', (f'%{search}%', f'%{search}%', limit))
    else:
        c.execute('''
            SELECT s.*, COUNT(DISTINCT a.id) as attendance_count
            FROM students s
            LEFT JOIN attendance a ON s.name = a.name
            GROUP BY s.id
            ORDER BY s.created_at DESC 
            LIMIT ?
        ''', (limit,))
    
    rows = c.fetchall()
    conn.close()
    
    return {
        "success": True,
        "count": len(rows),
        "data": [dict(row) for row in rows]
    }

@app.get("/api/v1/students/detected-faces")
async def get_detected_faces():
    """Get list of detected face names from model store"""
    try:
        import numpy as np
        from pathlib import Path
        
        model_path = Path(__file__).parent.parent / "model_store"
        labels_file = model_path / "labels.npy"
        
        if not labels_file.exists():
            return {
                "success": True,
                "data": []
            }
        
        labels = np.load(labels_file, allow_pickle=True)
        unique_names = sorted(set(labels))
        
        return {
            "success": True,
            "data": unique_names
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": []
        }

@app.post("/api/v1/students")
async def create_student(student: Dict[str, Any]):
    """Create a new student"""
    conn = get_db()
    c = conn.cursor()
    
    now = datetime.now().isoformat()
    
    try:
        c.execute('''
            INSERT INTO students (student_id, name, email, phone, department, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            student.get("student_id"),
            student.get("name"),
            student.get("email"),
            student.get("phone"),
            student.get("department"),
            now, now
        ))
        
        student_id = c.lastrowid
        conn.commit()
        
        return {"success": True, "id": student_id, "message": "Student created"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Student ID already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

# ============================================================
# Dashboard Endpoints
# ============================================================
@app.get("/api/v1/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    conn = get_db()
    c = conn.cursor()
    
    # Total students
    c.execute('SELECT COUNT(*) FROM students')
    total_students = c.fetchone()[0]
    
    # Today's attendance
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute('''
        SELECT COUNT(DISTINCT name) FROM attendance 
        WHERE DATE(timestamp) = ?
    ''', (today,))
    today_attendance = c.fetchone()[0]
    
    # This week's attendance
    week_start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    c.execute('''
        SELECT COUNT(DISTINCT name) FROM attendance 
        WHERE DATE(timestamp) >= ?
    ''', (week_start,))
    week_attendance = c.fetchone()[0]
    
    # Daily stats for last 7 days
    c.execute('''
        SELECT DATE(timestamp) as date, COUNT(DISTINCT name) as count
        FROM attendance 
        WHERE DATE(timestamp) >= date('now', '-7 days')
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
    ''')
    daily_stats = [{"date": r[0], "count": r[1]} for r in c.fetchall()]
    
    conn.close()
    
    return {
        "success": True,
        "data": {
            "total_students": total_students,
            "today_attendance": today_attendance,
            "week_attendance": week_attendance,
            "daily_stats": daily_stats,
            "active_connections": len(manager.active_connections)
        }
    }

# ============================================================
# Sessions Endpoints
# ============================================================
@app.post("/api/v1/sessions/start")
async def start_session(session: Dict[str, Any] = None):
    """Start a new attendance session"""
    conn = get_db()
    c = conn.cursor()
    
    now = datetime.now()
    session_name = session.get("name") if session else f"Session {now.strftime('%Y-%m-%d %H:%M')}"
    
    c.execute('''
        INSERT INTO attendance_sessions (session_name, course_id, started_at, status)
        VALUES (?, ?, ?, 'active')
    ''', (session_name, session.get("course_id") if session else None, now.isoformat()))
    
    session_id = c.lastrowid
    conn.commit()
    conn.close()
    
    await manager.broadcast({
        "type": "session_started",
        "session_id": session_id,
        "session_name": session_name
    })
    
    return {"success": True, "session_id": session_id, "session_name": session_name}

@app.get("/api/v1/sessions/active")
async def get_active_session():
    """Get currently active session"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM attendance_sessions 
        WHERE status = 'active' 
        ORDER BY started_at DESC 
        LIMIT 1
    ''')
    
    row = c.fetchone()
    conn.close()
    
    if row:
        return {"success": True, "data": dict(row)}
    return {"success": True, "data": None, "message": "No active session"}

@app.post("/api/v1/sessions/{session_id}/end")
async def end_session(session_id: int):
    """End an attendance session"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''
        UPDATE attendance_sessions 
        SET ended_at = ?, status = 'completed'
        WHERE id = ? AND status = 'active'
    ''', (datetime.now().isoformat(), session_id))
    
    success = c.rowcount > 0
    conn.commit()
    conn.close()
    
    if success:
        await manager.broadcast({
            "type": "session_ended",
            "session_id": session_id
        })
        return {"success": True, "message": "Session ended"}
    
    raise HTTPException(status_code=404, detail="Session not found or already ended")

# ============================================================
# Manual Attendance Management (NEW)
# ============================================================
@app.get("/api/v1/attendance/students-status")
async def get_students_attendance_status(date: Optional[str] = Query(None)):
    """Get all students with their attendance status for a specific date"""
    conn = get_db()
    c = conn.cursor()
    
    # Use today if no date provided
    target_date = date or datetime.now().strftime('%Y-%m-%d')
    
    # Get all students from label_map.json (model faces)
    model_path = Path(__file__).parent.parent / "model_store" / "label_map.json"
    model_students = []
    if model_path.exists():
        with open(model_path, 'r', encoding='utf-8') as f:
            label_map = json.load(f)
            model_students = list(label_map.values())
    
    # Get attendance records for the date
    c.execute('''
        SELECT name FROM attendance 
        WHERE DATE(timestamp) = ?
    ''', (target_date,))
    
    checked_in_names = set(row[0] for row in c.fetchall())
    conn.close()
    
    # Build student status list
    students_status = []
    for name in model_students:
        students_status.append({
            "name": name,
            "present": name in checked_in_names,
            "checked_by_camera": name in checked_in_names
        })
    
    return {
        "success": True,
        "date": target_date,
        "total_students": len(model_students),
        "present_count": len(checked_in_names),
        "absent_count": len(model_students) - len(checked_in_names),
        "data": students_status
    }

@app.post("/api/v1/attendance/manual-save")
async def save_manual_attendance(payload: Dict[str, Any], request: Request = None):
    """Save manual attendance (with switch toggles)"""
    conn = get_db()
    c = conn.cursor()
    
    target_date = payload.get("date", datetime.now().strftime('%Y-%m-%d'))
    students = payload.get("students", [])  # [{name: "xxx", present: true/false}]
    
    saved_count = 0
    removed_count = 0
    
    for student in students:
        name = student.get("name")
        present = student.get("present", False)
        
        if not name:
            continue
        
        # Check if already has record for this date
        c.execute('''
            SELECT id FROM attendance 
            WHERE name = ? AND DATE(timestamp) = ?
        ''', (name, target_date))
        
        existing = c.fetchone()
        
        if present:
            # Should be present
            if not existing:
                # Insert new record
                c.execute('''
                    INSERT INTO attendance (name, timestamp, confidence_score, camera_id)
                    VALUES (?, ?, ?, ?)
                ''', (name, f"{target_date}T09:00:00", 1.0, "manual"))
                saved_count += 1
        else:
            # Should be absent
            if existing:
                # Remove existing record
                c.execute('DELETE FROM attendance WHERE id = ?', (existing[0],))
                removed_count += 1
    
    conn.commit()
    conn.close()
    
    # Log manual attendance activity
    await log_activity(
        action_type="manual_attendance",
        description=f"บันทึกการเช็คชื่อแบบ Manual วันที่ {target_date}: เพิ่ม {saved_count} คน, ลบ {removed_count} คน",
        request=request,
        target_table="attendance",
        new_data={"date": target_date, "saved_count": saved_count, "removed_count": removed_count},
        success=True
    )
    
    # Broadcast update
    await manager.broadcast({
        "type": "attendance_manual_updated",
        "date": target_date,
        "saved": saved_count,
        "removed": removed_count
    })
    
    return {
        "success": True,
        "date": target_date,
        "saved_count": saved_count,
        "removed_count": removed_count,
        "message": f"Saved {saved_count}, removed {removed_count} records"
    }

@app.put("/api/v1/attendance/{record_id}")
async def update_attendance_record(record_id: int, payload: Dict[str, Any], request: Request = None):
    """Update a specific attendance record (for history editing)"""
    conn = get_db()
    c = conn.cursor()
    
    # Check if record exists
    c.execute('SELECT * FROM attendance WHERE id = ?', (record_id,))
    existing = c.fetchone()
    
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Record not found")
    
    # Update fields
    name = payload.get("name", existing["name"])
    timestamp = payload.get("timestamp", existing["timestamp"])
    modified_at = datetime.now().isoformat()
    
    # Store old data for logging
    old_data = {
        "name": existing["name"],
        "timestamp": existing["timestamp"]
    }
    new_data = {
        "name": name,
        "timestamp": timestamp
    }
    
    c.execute('''
        UPDATE attendance 
        SET name = ?, timestamp = ?, modified_at = ?
        WHERE id = ?
    ''', (name, timestamp, modified_at, record_id))
    
    conn.commit()
    conn.close()
    
    # Log edit activity
    await log_activity(
        action_type="attendance_edit",
        description=f"แก้ไขข้อมูลการเช็คชื่อ ID {record_id}: {existing['name']} → {name}",
        request=request,
        target_table="attendance",
        target_id=record_id,
        old_data=old_data,
        new_data=new_data,
        success=True
    )
    
    return {
        "success": True,
        "message": "Record updated",
        "id": record_id
    }

@app.delete("/api/v1/attendance/{record_id}")
async def delete_attendance_record(record_id: int, request: Request = None):
    """Delete a specific attendance record"""
    conn = get_db()
    c = conn.cursor()
    
    # Get record info before deletion for logging
    c.execute('SELECT * FROM attendance WHERE id = ?', (record_id,))
    record = c.fetchone()
    
    c.execute('DELETE FROM attendance WHERE id = ?', (record_id,))
    deleted = c.rowcount
    
    conn.commit()
    conn.close()
    
    if deleted > 0:
        # Log delete activity
        await log_activity(
            action_type="attendance_delete",
            description=f"ลบข้อมูลการเช็คชื่อ ID {record_id}: {record['name'] if record else 'Unknown'}",
            request=request,
            target_table="attendance",
            target_id=record_id,
            old_data={"name": record["name"], "timestamp": record["timestamp"]} if record else None,
            success=True
        )
        return {"success": True, "message": "Record deleted"}
    else:
        await log_activity(
            action_type="attendance_delete",
            description=f"พยายามลบข้อมูลการเช็คชื่อ ID {record_id} แต่ไม่พบข้อมูล",
            request=request,
            target_table="attendance",
            target_id=record_id,
            success=False
        )
        raise HTTPException(status_code=404, detail="Record not found")

@app.get("/api/v1/activity-logs")
async def get_activity_logs(
    limit: int = Query(50, ge=1, le=500),
    action_type: Optional[str] = Query(None),
    date: Optional[str] = Query(None)
):
    """Get activity logs with optional filtering"""
    conn = get_db()
    c = conn.cursor()
    
    # Build query with filters
    query = "SELECT * FROM activity_logs WHERE 1=1"
    params = []
    
    if action_type:
        query += " AND action_type = ?"
        params.append(action_type)
    
    if date:
        query += " AND DATE(timestamp) = ?"
        params.append(date)
    
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    
    c.execute(query, params)
    logs = []
    
    for row in c.fetchall():
        log = {
            "id": row["id"],
            "action_type": row["action_type"],
            "description": row["description"],
            "user_ip": row["user_ip"],
            "user_agent": row["user_agent"],
            "target_table": row["target_table"],
            "target_id": row["target_id"],
            "old_data": json.loads(row["old_data"]) if row["old_data"] else None,
            "new_data": json.loads(row["new_data"]) if row["new_data"] else None,
            "timestamp": row["timestamp"],
            "success": bool(row["success"])
        }
        logs.append(log)
    
    conn.close()
    
    return {
        "success": True,
        "data": logs,
        "count": len(logs)
    }

@app.get("/api/v1/model/students")
async def get_model_students():
    """Get list of students from model (label_map.json)"""
    model_path = Path(__file__).parent.parent / "model_store" / "label_map.json"
    
    if not model_path.exists():
        return {
            "success": True,
            "data": [],
            "count": 0
        }
    
    with open(model_path, 'r', encoding='utf-8') as f:
        label_map = json.load(f)
    
    students = [{"id": int(k), "name": v} for k, v in label_map.items()]
    
    return {
        "success": True,
        "data": students,
        "count": len(students)
    }

@app.get("/api/v1/attendance/by-date/{date}")
async def get_attendance_by_date(date: str):
    """Get attendance records for a specific date"""
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM attendance 
        WHERE DATE(timestamp) = ?
        ORDER BY timestamp DESC
    ''', (date,))
    
    rows = c.fetchall()
    conn.close()
    
    return {
        "success": True,
        "date": date,
        "count": len(rows),
        "data": [dict(row) for row in rows]
    }

# ============================================================
# State Endpoint (for debugging)
# ============================================================
@app.get("/api/v1/state")
async def get_state():
    """Get current application state"""
    return {
        "last_update": state.last_update,
        "last_detection": state.last_detection,
        "recent_logs_count": len(state.recent_logs),
        "recent_logs": state.recent_logs[:10],
        "websocket_clients": len(manager.active_connections)
    }

# ============================================================
# Run Server
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
