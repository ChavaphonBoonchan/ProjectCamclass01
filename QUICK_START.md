# 🚀 Quick Start Guide

คู่มือเริ่มต้นใช้งานระบบเช็คชื่อด้วยใบหน้าใน 5 นาที

## 📋 ข้อกำหนดเบื้องต้น

- ✅ Python 3.8+ ติดตั้งแล้ว
- ✅ Node.js 16+ ติดตั้งแล้ว  
- ✅ มีกล้องเชื่อมต่อกับคอมพิวเตอร์
- ✅ Git ติดตั้งแล้ว

## 🔧 ขั้นตอนที่ 1: Clone และ Setup

```bash
# Clone repository
git clone https://github.com/ChavaphonBoonchan/ProjectCamclass01.git
cd ProjectCamclass01

# สร้าง Python virtual environment
python -m venv .venv

# เปิดใช้งาน virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# ติดตั้ง Python dependencies
pip install -r requirements.txt
```

## 📦 ขั้นตอนที่ 2: ติดตั้ง Web Dependencies

```bash
cd web_app
npm install
cd ..
```

## ⚙️ ขั้นตอนที่ 3: ตั้งค่า Environment

```bash
# คัดลอกไฟล์ template
copy .env.example .env

# แก้ไขไฟล์ .env ด้วย notepad
notepad .env
```

**ตั้งค่าขั้นต่ำ:**
```env
# สำหรับ Telegram แจ้งเตือน (ไม่บังคับ)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

## 🚀 ขั้นตอนที่ 4: เริ่มระบบ

**เปิด 3 Terminal แยกกัน:**

### Terminal 1 - Backend Server
```bash
.venv\Scripts\activate
python app/server.py
```
➡️ **ผลลัพธ์:** Server จะรันที่ http://localhost:8000

### Terminal 2 - Web Frontend  
```bash
cd web_app
npm run dev
```
➡️ **ผลลัพธ์:** Web จะรันที่ http://localhost:3000

### Terminal 3 - Face Detection
```bash
.venv\Scripts\activate
python detection_prod/run_prod.py
```
➡️ **ผลลัพธ์:** กล้องจะเริ่มตรวจจับใบหน้า

## 🌐 ขั้นตอนที่ 5: เข้าใช้งานระบบ

1. **เปิด Web Browser**
2. **ไปที่:** http://localhost:3000
3. **คุณจะเห็น:** หน้าจอระบบเช็คชื่อ

### 🎯 หน้าต่างๆ ในระบบ:
- **หน้าหลัก (`/`)**: เช็คชื่อด้วยกล้อง
- **สถิติ (`/dashboard`)**: ดูสถิติการเข้าเรียน  
- **ประวัติ (`/history`)**: แก้ไขการเช็คชื่อ
- **นักเรียน (`/students`)**: จัดการรายชื่อ

## ✅ ทดสอบระบบ

### 1. ทดสอบกล้อง
- ✅ ตรวจสอบว่ากล้องทำงาน
- ✅ คุณจะเห็นภาพจากกล้องในหน้าเว็บ
- ✅ หากตรวจพบใบหน้า จะแสดงใน "Detected Faces"

### 2. ทดสอบเช็คชื่อ
- ✅ มองหน้ากล้อง
- ✅ คลิก "เช็คชื่อจากกล้อง"
- ✅ ระบบจะบันทึกการเช็คชื่อ

### 3. ทดสอบ Telegram (ถ้าตั้งค่าแล้ว)
```bash
python app/test_telegram.py
```

## 🛠️ แก้ไขปัญหาเบื้องต้น

### ❌ กล้องไม่ทำงาน
```bash
# ตรวจสอบกล้อง
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.read()[0] else 'Camera Error')"
```
**แก้ไข:** ปิดแอปอื่นที่ใช้กล้อง หรือเปลี่ยน CAMERA_ID ใน .env

### ❌ Web ไม่เปิด
```bash
# ตรวจสอบ port
netstat -an | findstr :3000
netstat -an | findstr :8000
```
**แก้ไข:** ตรวจสอบว่าทั้ง 3 service รันอยู่

### ❌ ไม่ตรวจจับใบหน้า
- **แสงสว่าง:** ตรวจสอบแสงเพียงพอ
- **มุมกล้อง:** หันหน้าเข้ากล้องตรงๆ
- **Model files:** ตรวจสอบไฟล์ใน `model_store/`

## 📈 ขั้นตอนต่อไป

### 🎓 เพิ่มข้อมูลนักเรียน
1. เพิ่มรูปนักเรียนใน `dataset/student_photos/`
2. อัพเดต `model_store/label_map.json`
3. รีสตาร์ทระบบ detection

### 📱 ตั้งค่า Telegram
1. สร้าง bot กับ @BotFather
2. ได้ Bot Token และ Chat ID
3. ใส่ใน `.env` file

### 📊 สำรวจฟีเจอร์
- **Dashboard:** ดูสถิติการเข้าเรียน
- **History:** แก้ไขประวัติการเช็คชื่อ
- **Students:** จัดการรายชื่อนักเรียน

## 📚 เอกสารเพิ่มเติม

สำหรับคำแนะนำโดยละเอียด ดูที่ไฟล์ `README.md`

---

**🎉 ยินดีด้วย! ระบบพร้อมใช้งานแล้ว**

---

## 📋 URLs สำคัญ

| Service | URL |
|---------|-----|
| Web App | http://localhost:3000 |
| API Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |
| WebSocket | ws://localhost:8000/ws |

---

## 🔧 API Endpoints

### Detection
- `POST /api/v1/ingest` - รับข้อมูลจากกล้อง

### Attendance
- `POST /api/v1/attendance/check` - บันทึกการเช็คชื่อ
- `GET /api/v1/attendance/history` - ดูประวัติการเช็คชื่อ
- `GET /api/v1/attendance/today` - ดูการเช็คชื่อวันนี้

### Students
- `GET /api/v1/students` - ดูรายชื่อนักเรียน
- `POST /api/v1/students` - เพิ่มนักเรียน

### Dashboard
- `GET /api/v1/dashboard/stats` - ดูสถิติ

### Sessions
- `POST /api/v1/sessions/start` - เริ่ม session
- `GET /api/v1/sessions/active` - ดู session ที่ active
- `POST /api/v1/sessions/{id}/end` - จบ session

### WebSocket
- `ws://localhost:8000/ws` - รับข้อมูล real-time

---

## 🧪 ทดสอบระบบ

```bash
# ทดสอบ Telegram (ถ้าตั้งค่าแล้ว)
python app/test_telegram.py

# ตรวจสอบ API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/activity-logs?limit=5
```

---

## 📁 โครงสร้างไฟล์

```
ProjectCamclass01/
├── 📁 app/                 # Backend FastAPI server
│   └── server.py          # Main server file
├── 📁 web_app/            # Frontend Nuxt.js application  
│   ├── pages/
│   └── nuxt.config.ts
├── 📁 detection_prod/     # Production detection scripts
│   ├── config.json        # Detection configuration
│   └── run_prod.py        # Face detection program
├── 📁 face_common/        # Face recognition utilities
├── 📁 model_store/        # Models และ label_map.json
│   └── label_map.json
├── 📁 database/           # SQLite database files
│   └── attendance.db      # Main database
├── 📁 dataset/           # Training photos
│   └── student_photos/
├── 📄 .env.example       # Environment template
├── 📄 requirements.txt   # Python dependencies
├── 📄 README.md         # คู่มือโดยละเอียด
└── 📄 QUICK_START.md    # คู่มือนี้
```

---

## ⚠️ Troubleshooting

### Backend ไม่ทำงาน
```bash
# ตรวจสอบ port 8000
netstat -an | findstr :8000

# ลองรันใหม่
.venv\Scripts\activate
python app/server.py
```

### WebSocket ไม่เชื่อมต่อ
1. ตรวจสอบว่า backend ทำงาน
2. ดู browser console (F12)
3. ตรวจสอบ firewall

### กล้องไม่ทำงาน
1. เปลี่ยน `camera_index` ใน `detection_prod/config.json`
2. ลอง 0, 1, 2
3. ตรวจสอบว่ากล้องไม่ถูกใช้งานโดยโปรแกรมอื่น

### ไม่มีโมเดล
1. ตรวจสอบ `model_store/` มีไฟล์:
   - model.pkl
   - embeddings.npy
   - labels.npy
2. ถ้าไม่มี ต้องเทรนโมเดลก่อน

---

## 🎯 Flow การทำงาน

```
[กล้อง] → [Detection] → [Backend API] → [WebSocket] → [Web App]
                              ↓
                         [SQLite DB]
```

1. **กล้อง** จับภาพใบหน้า
2. **Detection** ตรวจจับและระบุตัวตน
3. **Backend** รับข้อมูลและ broadcast ไป WebSocket
4. **Web App** แสดงผลแบบ real-time
5. **SQLite** เก็บข้อมูลการเช็คชื่อ

---

## ✅ เมื่อระบบทำงานได้

1. เปิด http://localhost:3000
2. เห็นภาพจากกล้อง (ถ้ารัน detection)
3. เห็นกรอบรอบใบหน้า
4. กด "Check Attendance" เพื่อบันทึก
5. ดูสถิติที่ Dashboard

---

## 📞 Support

หากมีปัญหา:
1. รัน `python test_system_complete.py` เพื่อตรวจสอบ
2. ดู error ใน terminal
3. ตรวจสอบ browser console (F12)
