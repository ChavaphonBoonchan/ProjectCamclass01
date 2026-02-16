# 🎯 Face Attendance System (Cam-Class01)

ระบบเช็คชื่อด้วยการตรวจจับใบหน้าแบบเรียลไทม์ พร้อมเว็บอินเตอร์เฟซและการแจ้งเตือนผ่าน Telegram

## ✨ Features

- **🔍 Real-time Face Detection**: ใช้ OpenCV และ face recognition สำหรับการตรวจจับแบบเรียลไทม์
- **💻 Web Dashboard**: อินเตอร์เฟซ Vue.js/Nuxt.js สำหรับจัดการการเช็คชื่อ
- **📱 Telegram Integration**: แจ้งเตือนอัตโนมัติเมื่อมีการเช็คชื่อ
- **🗄️ Database Management**: ฐานข้อมูล SQLite พร้อมประวัติการเช็คชื่อ
- **✋ Manual Override**: สามารถเช็คชื่อด้วยตนเองได้
- **📷 Multi-session Support**: รองรับการเช็คชื่อหลายครั้งต่อวัน
- **📊 Activity Logging**: บันทึกและรายงานการกระทำทั้งหมดผ่าน Telegram

## 🚀 Quick Setup Guide

### 📋 ข้อกำหนดระบบ

- **Python 3.8+**
- **Node.js 16+**
- **Webcam/Camera**
- **Telegram Account** (สำหรับการแจ้งเตือน)

### 🔧 การติดตั้งแบบครบวงจร

#### 1️⃣ **Clone โปรเจคต์**
```bash
git clone https://github.com/ChavaphonBoonchan/ProjectCamclass01.git
cd ProjectCamclass01
```

#### 2️⃣ **ติดตั้ง Python Environment**
```bash
# สร้าง virtual environment
python -m venv .venv

# เปิดใช้งาน virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# ติดตั้ง dependencies
pip install -r requirements.txt
```

#### 3️⃣ **ติดตั้ง Web App Dependencies**
```bash
cd web_app
npm install
cd ..
```

#### 4️⃣ **ตั้งค่า Environment Variables**
```bash
# คัดลอกไฟล์ตัวอย่าง
copy .env.example .env

# แก้ไขไฟล์ .env ด้วย text editor
notepad .env
```

#### 5️⃣ **ตั้งค่า Telegram Bot**

**สร้าง Telegram Bot:**
1. เปิด Telegram แล้วหา `@BotFather`
2. ส่งคำสั่ง `/newbot`
3. ตั้งชื่อ bot และ username
4. คัดลอก **Bot Token** ที่ได้

**หา Chat ID:**
1. ส่งข้อความไปหา bot ที่สร้าง
2. เปิดลิงก์: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. หา `"chat":{"id":` แล้วคัดลอกตัวเลข **Chat ID**

**อัพเดตไฟล์ .env:**
```env
TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
TELEGRAM_CHAT_ID=your_actual_chat_id_here
```

#### 6️⃣ **เตรียมข้อมูลนักเรียน**
```bash
# สร้างโฟลเดอร์สำหรับรูปนักเรียน
mkdir dataset
mkdir dataset/student_photos

# เพิ่มรูปนักเรียนใน dataset/student_photos/
# ตั้งชื่อไฟล์เป็น: student_name_1.jpg, student_name_2.jpg
```

#### 7️⃣ **รันระบบ**

**เปิด 3 Terminal แยกกัน:**

**Terminal 1 - Backend Server:**
```bash
.venv\Scripts\activate
python app/server.py
```

**Terminal 2 - Web Frontend:**
```bash
cd web_app
npm run dev
```

**Terminal 3 - Face Detection:**
```bash
.venv\Scripts\activate
python detection_prod/run_prod.py
```

#### 8️⃣ **เข้าใช้งานระบบ**
- **เว็บไซต์:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **Backend Health:** http://localhost:8000/health

## 📱 การใช้งาน

### 🖥️ Web Interface

1. **หน้าเช็คชื่อ** (`/`): แสดงกล้องและใบหน้าที่ตรวจพบ
2. **หน้าสถิติ** (`/dashboard`): ดูสถิติการเข้าเรียน
3. **หน้าแก้ไขประวัติ** (`/history`): แก้ไขการเช็คชื่อย้อนหลัง
4. **หน้ารายชื่อนักเรียน** (`/students`): ดูรายชื่อนักเรียนในระบบ

### 📊 ฟีเจอร์หลัก

- ✅ **เช็คชื่อหลายครั้งต่อวัน** (ป้องกัน spam ภายใน 5 นาที)
- ✅ **แสดงจำนวนครั้งที่เช็คชื่อ** แต่ละคน
- ✅ **Telegram แจ้งเตือนภาษาไทย** พร้อมสถิติ
- ✅ **แก้ไขประวัติการเช็คชื่อ** ได้
- ✅ **เพิ่มการเช็คชื่อด้วยมือ** ได้

## 🔧 การปรับแต่ง

### 📝 เพิ่มนักเรียนใหม่

1. เพิ่มรูปนักเรียนใน `dataset/student_photos/`
2. อัพเดต `model_store/label_map.json`
3. รีสตาร์ทระบบ detection

### ⚙️ ปรับแต่งการตรวจจับ

แก้ไขไฟล์ `detection_prod/config.json`:
```json
{
  "camera_index": 0,
  "confidence_threshold": 0.7,
  "fps_limit": 30,
  "model_dir": "model_store",
  "api_base": "http://localhost:8000"
}
```

**หมายเหตุ:** ไฟล์ `.env` ใช้สำหรับ server config (Telegram) เท่านั้น

## 🛠️ Troubleshooting

### ❌ ปัญหาที่พบบ่อย

**1. กล้องไม่ทำงาน**
```bash
# ตรวจสอบกล้อง
python -c "import cv2; print(cv2.VideoCapture(0).read())"
```

**2. ไม่สามารถตรวจจับใบหน้าได้**
- ตรวจสอบแสงสว่าง
- ตรวจสอบมุมกล้อง
- ตรวจสอบไฟล์รูปนักเรียนใน dataset

**3. Telegram ไม่แจ้งเตือน**
```bash
# ทดสอบ Telegram
python app/test_telegram.py
```

**4. Web ไม่เปิด**
```bash
# ตรวจสอบ port
netstat -an | findstr :3000
netstat -an | findstr :8000
```

### 📋 การตรวจสอบระบบ

```bash
# ตรวจสอบ Python packages
pip list | findstr opencv
pip list | findstr face-recognition

# ตรวจสอบ Node.js
node --version
npm --version

# ตรวจสอบไฟล์สำคัญ
dir model_store
dir database
dir .env
```

## 🏗️ โครงสร้างโปรเจคต์

```
camclass01/
├── 📁 app/                 # Backend FastAPI server
├── 📁 web_app/            # Frontend Nuxt.js application  
├── 📁 detection_prod/     # Production detection scripts
├── 📁 face_common/        # Face recognition utilities
├── 📁 model_store/        # Models และ label_map.json
├── 📁 database/           # SQLite database files
├── 📁 bin/               # Start scripts (.bat files)
├── 📁 tools/             # Utility scripts
├── 📁 dataset/           # Training photos
├── 📄 .env.example       # Environment template
├── 📄 requirements.txt   # Python dependencies
├── 📄 README.md         # คู่มือนี้
└── 📄 QUICK_START.md    # คู่มือเริ่มต้นเร็ว
```

## 🔒 Security Notes

- ไฟล์ `.env` จะไม่ถูก commit ไป Git (มี sensitive data)
- ใช้ `.env.example` เป็นแม่แบบสำหรับการตั้งค่า
- Telegram Bot Token ควรเก็บเป็นความลับ

## 📞 Support

หากมีปัญหาการใช้งาน:
1. ตรวจสอบ Troubleshooting section
2. ดู logs ใน terminal
3. ตรวจสอบไฟล์ `.env` ว่าถูกต้อง

## 📄 License

MIT License - ใช้งานได้อย่างอิสระโดยห้ามใช้ในเชิงพาณิชย์