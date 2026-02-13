# GPU (CUDA) Setup Guide for Face Recognition System

## การตั้งค่า NVIDIA GPU สำหรับระบบ Face Recognition

### ข้อกำหนดเบื้องต้น (Prerequisites)

1. **NVIDIA GPU** ที่รองรับ CUDA (แนะนำ RTX series หรือใหม่กว่า)
2. **CUDA Toolkit** เวอร์ชัน 11.x หรือ 12.x
3. **cuDNN** library
4. **Python 3.11 หรือ 3.12** (64-bit)

---

## ขั้นตอนการติดตั้ง (Installation Steps)

### 1. ตรวจสอบ GPU ของคุณ

เปิด Command Prompt หรือ PowerShell และรันคำสั่ง:

```powershell
nvidia-smi
```

คุณควรเห็นข้อมูล GPU ของคุณ เช่น:
- GPU name (เช่น RTX 3060, RTX 4070)
- CUDA Version
- Driver Version

### 2. ติดตั้ง CUDA Toolkit (ถ้ายังไม่มี)

1. ดาวน์โหลด CUDA Toolkit จาก:
   https://developer.nvidia.com/cuda-downloads

2. เลือก:
   - Operating System: Windows
   - Architecture: x86_64
   - Version: Windows 10/11
   - Installer Type: exe (local)

3. ติดตั้งตามขั้นตอน (Express Installation)

4. ตรวจสอบการติดตั้ง:
   ```powershell
   nvcc --version
   ```

### 3. ติดตั้ง cuDNN (ถ้ายังไม่มี)

1. ดาวน์โหลด cuDNN จาก:
   https://developer.nvidia.com/cudnn
   (ต้องสมัคร NVIDIA Developer account ฟรี)

2. แตกไฟล์และคัดลอกไฟล์ไปยัง CUDA directory:
   - คัดลอก `bin\cudnn*.dll` ไปที่ `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.x\bin`
   - คัดลอก `include\cudnn*.h` ไปที่ `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.x\include`
   - คัดลอก `lib\x64\cudnn*.lib` ไปที่ `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.x\lib\x64`

### 4. ติดตั้ง onnxruntime-gpu

ใน virtual environment ของโปรเจค:

```powershell
# เปิด virtual environment
.venv\Scripts\activate

# ถอนการติดตั้ง onnxruntime แบบ CPU (ถ้ามี)
pip uninstall onnxruntime -y

# ติดตั้ง onnxruntime-gpu
pip install onnxruntime-gpu

# ติดตั้ง GPU monitoring tools
pip install gputil psutil
```

### 5. ตรวจสอบการติดตั้ง

สร้างไฟล์ `test_gpu.py`:

```python
import onnxruntime as ort

print("Available providers:", ort.get_available_providers())

# ควรเห็น 'CUDAExecutionProvider' ในรายการ
if 'CUDAExecutionProvider' in ort.get_available_providers():
    print("✓ GPU (CUDA) is available!")
else:
    print("✗ GPU (CUDA) is NOT available")
```

รันคำสั่ง:
```powershell
python test_gpu.py
```

---

## การใช้งาน GPU ในโปรเจค

### วิธีที่ 1: Auto-detect (แนะนำ)

ระบบจะตรวจจับ GPU อัตโนมัติ ไม่ต้องตั้งค่าอะไรเพิ่ม

ในไฟล์ `config.example.json`:
```json
{
  "provider": "auto",
  ...
}
```

### วิธีที่ 2: กำหนด Provider เอง

ในไฟล์ `config.example.json`:
```json
{
  "provider": "CUDAExecutionProvider",
  ...
}
```

หรือใช้ command line argument:
```powershell
python -m detection_debug.debug_gui --config .\detection_debug\config.example.json --provider CUDAExecutionProvider
```

---

## การตรวจสอบประสิทธิภาพ

### ใน Debug GUI

เมื่อเปิด Debug GUI คุณจะเห็น:
- **GPU Status**: แสดงชื่อ GPU และสถานะ
- **GPU Utilization**: % การใช้งาน GPU
- **GPU Memory**: หน่วยความจำที่ใช้/ทั้งหมด
- **Inference Time**: เวลาในการประมวลผลแต่ละเฟรม (ms)

### เปรียบเทียบ CPU vs GPU

**CPU Mode:**
- Inference time: ~100-300 ms/frame
- FPS: ~3-10 fps

**GPU Mode (RTX 3060+):**
- Inference time: ~10-30 ms/frame
- FPS: ~30-60 fps

---

## การแก้ปัญหา (Troubleshooting)

### ปัญหา: ไม่เห็น CUDAExecutionProvider

**แก้ไข:**
1. ตรวจสอบว่าติดตั้ง `onnxruntime-gpu` แล้ว (ไม่ใช่ `onnxruntime`)
   ```powershell
   pip list | findstr onnxruntime
   ```
   ควรเห็น `onnxruntime-gpu`

2. ตรวจสอบ CUDA version compatibility:
   - onnxruntime-gpu 1.16.x รองรับ CUDA 11.8, 12.x
   - ตรวจสอบที่: https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html

### ปัญหา: Out of Memory

**แก้ไข:**
1. ลด `resize_max` ในไฟล์ config (เช่น จาก 0 เป็น 640 หรือ 960)
2. ลด `det_size` ใน face_engine.py (default: 640x640)
3. ปิดโปรแกรมอื่นที่ใช้ GPU

### ปัญหา: GPU Utilization ต่ำ

**สาเหตุ:**
- Bottleneck อาจอยู่ที่ Camera I/O หรือ CPU preprocessing
- ลอง disable `send_image` ใน config เพื่อลดภาระ

**แก้ไข:**
1. เพิ่ม `fps_limit` ใน config (เช่น 30)
2. ปรับ `resize_max` ให้เหมาะสม

### ปัญหา: Driver version mismatch

**แก้ไข:**
1. อัพเดท NVIDIA Driver ให้เป็นเวอร์ชันล่าสุด:
   https://www.nvidia.com/Download/index.aspx

2. Restart เครื่อง

---

## Performance Tips

### 1. Optimize Config Settings

```json
{
  "provider": "auto",
  "resize_max": 960,        // ลดขนาดภาพก่อนประมวลผล
  "min_face_size": 60,      // เพิ่มขนาดใบหน้าขั้นต่ำ
  "fps_limit": 30,          // จำกัด FPS
  "send_interval_ms": 500,  // ส่งข้อมูลทุก 500ms
  "send_image": false       // ปิดการส่งภาพถ้าไม่จำเป็น
}
```

### 2. Batch Processing (สำหรับ Production)

ถ้ามีหลายกล้อง ให้รัน process แยกกันแทนที่จะรวมกัน

### 3. Model Optimization

InsightFace ใช้ ONNX models ที่ optimize แล้ว แต่ถ้าต้องการเร็วขึ้นอีก:
- ใช้โมเดลเล็กกว่า (buffalo_s แทน buffalo_l)
- ลด det_size

---

## เปรียบเทียบ Providers

| Provider | Speed | Accuracy | Requirements |
|----------|-------|----------|--------------|
| CPUExecutionProvider | ⭐⭐ | ⭐⭐⭐⭐⭐ | CPU only |
| CUDAExecutionProvider | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | NVIDIA GPU + CUDA |

---

## สรุป

1. ✅ ติดตั้ง CUDA Toolkit และ cuDNN
2. ✅ ติดตั้ง `onnxruntime-gpu`
3. ✅ ตั้งค่า `"provider": "auto"` ในไฟล์ config
4. ✅ รัน Debug GUI และตรวจสอบ GPU status
5. ✅ ปรับแต่ง config ให้เหมาะกับระบบ

หากมีปัญหาหรือข้อสงสัย สามารถดูข้อมูลเพิ่มเติมได้ที่:
- ONNX Runtime CUDA: https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html
- InsightFace: https://github.com/deepinsight/insightface
