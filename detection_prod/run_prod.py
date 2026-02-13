from __future__ import annotations

import argparse
import asyncio
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import sys
from pathlib import Path

# Add parent directory to path for face_common import
sys.path.append(str(Path(__file__).parent.parent))

import cv2
import requests
import websockets

from face_common.config import load_config
from face_common.face_engine import InsightFaceEngine
from face_common.image_utils import bgr_to_jpeg_base64, resize_max_side, draw_face_box
from face_common.recognizer import FaceRecognizer


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


async def send_ws(endpoint: str, payload: Dict[str, Any]) -> None:
    try:
        async with websockets.connect(endpoint, ping_interval=20, ping_timeout=20) as ws:
            await ws.send(__import__("json").dumps(payload))
    except Exception as e:
        print(f"[WS Error] {e}")


def send_http(endpoint: str, payload: Dict[str, Any]) -> None:
    try:
        requests.post(endpoint, json=payload, timeout=0.5)
    except Exception:
        pass


async def main_async() -> None:
    print("=" * 60)
    print("🚀 Face Recognition Production (Headless)")
    print("=" * 60)
    
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="detection_debug/config.example.json", help="Path to config file")
    ap.add_argument("--provider", default=None, help='Override provider, e.g. "CUDAExecutionProvider"')
    args = ap.parse_args()

    # 1. Load Config
    try:
        cfg = load_config(args.config)
        print(f"✅ Config loaded: {args.config}")
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return

    # 2. Setup Face Engine (GPU/CPU)
    provider_to_use = args.provider or getattr(cfg, "provider", "auto")
    print(f"⚡ Initializing Engine with provider: {provider_to_use}")
    
    try:
        engine = InsightFaceEngine(provider=provider_to_use)
    except Exception as e:
        print(f"❌ Failed to load InsightFace: {e}")
        return

    # 3. Setup Recognizer
    try:
        recog = FaceRecognizer(cfg.model_dir, threshold=cfg.threshold, unknown_label=cfg.unknown_label)
        people_count = len(recog.label_map) if recog.label_map else 0
        print(f"📚 Loaded Recognizer with {people_count} known people")
    except Exception as e:
        print(f"❌ Failed to load Recognizer: {e}")
        return

    # 4. Open Camera
    print(f"📹 Opening Camera index: {cfg.camera_index}")
    
    # Try to open camera with fallback
    cap = cv2.VideoCapture(int(cfg.camera_index))
    if not cap.isOpened():
        print(f"❌ Failed to open camera {cfg.camera_index}")
        # Try to find available cameras
        for i in range(3):
            test_cap = cv2.VideoCapture(i)
            if test_cap.isOpened():
                test_cap.release()
                print(f"📹 Found available camera at index {i}")
                cfg.camera_index = i
                cap = cv2.VideoCapture(i)
                break
        else:
            print("❌ No cameras found!")
            return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(cfg.width))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(cfg.height))

    max_faces = getattr(cfg, "max_faces", 20)
    print(f"🛡️ Max Faces Limit: {max_faces}")
    print(f"📡 Send Mode: {cfg.send_mode}")
    print(f"⏱️ Send Interval: {cfg.send_interval_ms} ms")
    
    print("=" * 60)
    print("✅ System Ready - Starting loop...")
    print("=" * 60)

    last_send_t = 0.0
    frame_count = 0
    fps_start_time = time.time()
    
    # Send interval in seconds
    interval_sec = float(cfg.send_interval_ms) / 1000.0

    while True:
        loop_start = time.time()
        
        # Read frame
        ok, frame = cap.read()
        if not ok or frame is None:
            await asyncio.sleep(0.01)
            continue
            
        frame_count += 1
        
        # FPS Calculation (every 5 seconds)
        if frame_count % 150 == 0:
            elapsed = time.time() - fps_start_time
            fps = frame_count / elapsed
            print(f"📊 Status: {fps:.1f} FPS | Camera: {cfg.camera_id}")
            frame_count = 0
            fps_start_time = time.time()

        # FPS Limiter
        if cfg.fps_limit and cfg.fps_limit > 0:
            target_time = 1.0 / float(cfg.fps_limit)
            elapsed = time.time() - loop_start
            wait = target_time - elapsed
            if wait > 0:
                await asyncio.sleep(wait)

        # Skip processing if we sent recently and don't need to process every frame
        # (For production, we prioritize sending data over processing every single frame if lagging)
        time_since_last_send = time.time() - last_send_t
        if time_since_last_send < interval_sec:
            # Skip heavy processing, just wait for next meaningful frame
            await asyncio.sleep(0.005)
            continue

        # Resize for performance
        img, _scale = resize_max_side(frame, cfg.resize_max)

        # Detect
        try:
            dets = engine.detect_and_embed(img, min_face_size=cfg.min_face_size, max_faces=max_faces)
        except Exception as e:
            print(f"⚠️ Detection error: {e}")
            continue

        known_faces: List[Dict[str, Any]] = []
        unknown_count = 0

        # Optional annotated image
        annotated = img if cfg.send_image else None

        # Recognize
        for d in dets:
            rr = recog.recognize(d.embedding)
            if rr.known:
                known_faces.append({"name": rr.name, "confidence": float(rr.confidence)})
            else:
                unknown_count += 1
                
            if annotated is not None:
                x1, y1, x2, y2 = d.bbox_xyxy
                draw_face_box(annotated, x1, y1, x2, y2, rr.name, rr.confidence, rr.known)

        total_faces = len(dets)

        # Prepare payload
        current_time = time.time()
        last_send_t = current_time

        img_b64 = bgr_to_jpeg_base64(annotated, quality=cfg.jpeg_quality) if annotated is not None else None
        
        payload: Dict[str, Any] = {
            "timestamp": now_iso(),
            "camera_id": cfg.camera_id,
            "total_faces": total_faces,
            "known_faces": known_faces,
            "unknown_faces": unknown_count,
            "stream_image": img_b64,
        }

        # Send
        if cfg.send_mode == "ws":
            await send_ws(cfg.endpoint_ws, payload)
        else:
            send_http(cfg.endpoint_http, payload)


def main() -> None:
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
    except Exception as e:
        print(f"\n❌ Critical Error: {e}")


if __name__ == "__main__":
    main()
