# วิธีรันโปรแกรมให้ใช้ GPU

## ✅ ระบบของคุณพร้อมใช้งาน GPU แล้ว!

- **GPU**: NVIDIA GeForce RTX 3050 6GB Laptop GPU
- **CUDA**: Version 13.1
- **Provider**: CUDAExecutionProvider
- **Status**: GPU Ready! 🚀

---

## 🚀 วิธีรันโปรแกรม (3 วิธี)

### วิธีที่ 1: ใช้ PowerShell Script (ง่ายที่สุด) ⭐

#### รัน Debug GUI:
```powershell
.\run_debug_gpu.ps1
```

#### รัน Dashboard:
```powershell
.\run_dashboard.ps1
```

---

### วิธีที่ 2: ใช้ Command Line

#### รัน Debug GUI:
```powershell
.venv\Scripts\python.exe -m detection_debug.debug_gui --config .\detection_debug\config.example.json
```

#### รัน Dashboard:
```powershell
.venv\Scripts\python.exe -m dashboard.server --host 0.0.0.0 --port 8000
```

---

### วิธีที่ 3: Activate Virtual Environment แล้วรัน

```powershell
# Activate virtual environment
.venv\Scripts\activate

# รัน Debug GUI
python -m detection_debug.debug_gui --config .\detection_debug\config.example.json

# หรือ รัน Dashboard
python -m dashboard.server --host 0.0.0.0 --port 8000
```

---

## ⚠️ สิ่งที่ต้องระวัง

### ❌ อย่าทำ:
```powershell
# อย่ารันแบบนี้ (จะใช้ Python ของระบบ ไม่ใช่ของ venv)
python -m detection_debug.debug_gui ...
```

### ✅ ทำแบบนี้:
```powershell
# ใช้ Python จาก virtual environment
.venv\Scripts\python.exe -m detection_debug.debug_gui ...

# หรือ activate venv ก่อน
.venv\Scripts\activate
python -m detection_debug.debug_gui ...
```

---

## 🎯 ตรวจสอบว่าใช้ GPU หรือไม่

เมื่อรันโปรแกรม ดูที่ console output:

```
[InsightFace] Using provider: CUDAExecutionProvider  ✅ ใช้ GPU
[InsightFace] Using provider: CPUExecutionProvider   ❌ ใช้ CPU
```

หรือดูใน Debug GUI:
- แผง **System** ด้านขวา
- ดูที่ **GPU Status**
- ควรเห็น "NVIDIA GeForce RTX 3050"

---

## 📊 Performance ที่คาดหวัง

### กับ GPU (RTX 3050):
- **FPS**: 30-60 fps
- **Inference Time**: 10-30 ms
- **GPU Utilization**: 40-80%

### กับ CPU (ถ้าไม่ใช้ GPU):
- **FPS**: 5-15 fps
- **Inference Time**: 60-200 ms
- **CPU Usage**: 50-100%

---

## 🔧 Troubleshooting

### ปัญหา: ยังใช้ CPU อยู่

**สาเหตุ**: ไม่ได้ใช้ Python จาก virtual environment

**แก้ไข**:
1. ใช้ `.venv\Scripts\python.exe` แทน `python`
2. หรือ activate venv ก่อน: `.venv\Scripts\activate`

### ปัญหา: ไม่เห็น GPU status ใน GUI

**สาเหตุ**: ยังไม่ได้ติดตั้ง gputil

**แก้ไข**:
```powershell
.venv\Scripts\python.exe -m pip install gputil psutil
```

### ปัญหา: Out of Memory

**แก้ไข**: แก้ไขไฟล์ `detection_debug\config.example.json`
```json
{
  "resize_max": 640,     // ลดจาก 0 เป็น 640
  "min_face_size": 80    // เพิ่มจาก 40 เป็น 80
}
```

---

## 🎉 เสร็จแล้ว!

ตอนนี้คุณพร้อมใช้งานระบบ Face Recognition พร้อม GPU แล้ว!

รันด้วยคำสั่ง:
```powershell
.\run_debug_gpu.ps1
```

สนุกกับความเร็ว 3-10x! 🚀
