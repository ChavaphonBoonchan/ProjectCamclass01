## ภาพรวมโปรเจค (Project Guide)

TH: เอกสารนี้อธิบาย “โครงสร้าง + การทำงานของโค้ด” ในโปรเจค Face Recognition System  
EN: This document explains how the codebase is structured and how data flows end-to-end.

---

## 1) Architecture / Data Flow

TH (ภาพรวม):
- (1) **Training**: อ่านภาพจาก `dataset/<person_name>/*.jpg|png` → ตรวจจับหน้า → สร้าง embedding → เทรน classifier/เก็บ gallery → บันทึกไฟล์เข้า `model_store/`
- (2.1) **Debug GUI**: เปิดกล้อง → detect+embed → recognize → วาดกรอบ/ชื่อ/FPS → (option) ส่ง event ไป Dashboard
- (2.2) **Production**: เปิดกล้องแบบ headless → detect+embed → recognize → ส่ง event ไป Dashboard (HTTP/WS) แบบเบา
- (3) **Dashboard**: รับ event ผ่าน HTTP → broadcast ผ่าน WebSocket → UI แสดงผล realtime + log table

EN (overview):
Training produces a model gallery/classifier; Detection modules generate events; Dashboard receives and visualizes.

---

## 2) Folder Structure (สำคัญ)

- `training/`
  - `train.py`: CLI เทรนโมเดลจาก dataset folder
- `face_common/` (shared)
  - `face_engine.py`: `InsightFaceEngine` เรียก InsightFace เพื่อ **detect + embedding**
  - `recognizer.py`: `FaceRecognizer` ทำ mapping embedding → known/unknown ด้วย threshold
  - `config.py`: schema ของ config + load/save
  - `image_utils.py`: resize, base64 jpeg, draw bbox+label
- `detection_debug/`
  - `debug_gui.py`: OpenCV window + hotkeys + save config + simulate production (ส่ง event)
  - `config.example.json`: config ตัวอย่างสำหรับ debug/prod
- `detection_prod/`
  - `run_prod.py`: headless optimized sender (HTTP/WS) + toggle base64 image
- `dashboard/`
  - `server.py`: FastAPI receiver + WS broadcaster + serve static UI
  - `web/`: `index.html`, `app.js` UI
- `scripts/`
  - `run_dashboard.ps1`: รัน dashboard
  - `run_dashboard_and_debug.ps1`: เปิด 2 terminal (dashboard + debug)
  - `run_dashboard_and_prod.ps1`: เปิด 2 terminal (dashboard + prod)

---

## 3) Training (1) — How it works

1. อ่านรูปทั้งหมดจาก `dataset/<person>/...`
2. ข้าม folder `unknown/` (ถ้ามี)
3. ใช้ `InsightFaceEngine.detect_and_embed()` เพื่อได้ embedding (normalized)
4. บันทึก:
   - `model_store/embeddings.npy`, `model_store/labels.npy`
   - `model_store/label_map.json`
   - `model_store/model.pkl` (ถ้าเลือก `--classifier svm`)

---

## 4) Recognition / Unknown rule (สำคัญ)

TH: “unknown” = ใบหน้าที่ **ไม่เหมือน** คนในโมเดล “เกิน threshold”
- cosine similarity: ถ้า `best_sim < threshold` → `unknown`
- SVM probability: ถ้า `probability < threshold` → `unknown`

EN: Unknown means “not similar enough to any known identity given the threshold”.

Tips:
- ถ้า unknown เยอะเกินไป → ลด `threshold` ลง
- ถ้าติดชื่อผิด (false positive) → เพิ่ม `threshold` ขึ้น

---

## 4.1) CUDA / GPU

- ถ้ามี NVIDIA RTX และต้องการเร่งด้วย GPU:
  - ติดตั้ง CUDA Runtime แล้วรัน: `pip install onnxruntime-gpu==1.23.2`
  - ตั้งค่าใน config (debug/prod): `"provider": "CUDAExecutionProvider"`
- ค่าเริ่มต้นเป็น CPU: `"provider": "CPUExecutionProvider"`

---

## 5) Event payload / API

Detection → Dashboard ส่ง JSON:

```json
{
  "timestamp": "2026-01-20T12:34:56.123Z",
  "camera_id": "cam01",
  "total_faces": 3,
  "known_faces": [{"name":"Alice","confidence":0.92}],
  "unknown_faces": 2,
  "stream_image": "base64-jpeg-or-null"
}
```

Endpoints:
- HTTP ingest: `POST /api/v1/ingest`
- State: `GET /api/v1/state`
- WebSocket broadcast: `/ws`

---

## 6) Node-RED integration

TH:
- ใช้ Node-RED `http in` (POST) → `json` → `function`/`switch` → `ui_*` nodes
- ตั้ง URL ให้ตรงกับ Dashboard หรือจะให้ Node-RED เป็น receiver แทนก็ได้

EN:
- Node-RED can receive the same payload via HTTP In, then display via dashboard nodes.

