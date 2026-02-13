from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import cv2
import numpy as np
import requests
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from face_common.config import DetectionConfig, load_config, save_config
from face_common.face_engine import InsightFaceEngine, is_gpu_available, get_available_providers
from face_common.image_utils import bgr_to_jpeg_base64, draw_face_box, resize_max_side
from face_common.recognizer import FaceRecognizer


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def send_http(endpoint: str, payload: Dict[str, Any]) -> None:
    try:
        requests.post(endpoint, json=payload, timeout=1.0)
    except Exception:
        pass


def get_gpu_info() -> Dict[str, Any]:
    """Get GPU information if available"""
    info = {
        "available": False,
        "name": "N/A",
        "memory_used": 0,
        "memory_total": 0,
        "utilization": 0
    }
    
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]  # Use first GPU
            info["available"] = True
            info["name"] = gpu.name
            info["memory_used"] = gpu.memoryUsed
            info["memory_total"] = gpu.memoryTotal
            info["utilization"] = gpu.load * 100
    except Exception:
        pass
    
    return info


def get_cpu_memory_info() -> Dict[str, Any]:
    """Get CPU and RAM information"""
    info = {
        "cpu_percent": 0,
        "memory_percent": 0,
        "memory_used_gb": 0,
        "memory_total_gb": 0
    }
    
    try:
        import psutil
        info["cpu_percent"] = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        info["memory_percent"] = mem.percent
        info["memory_used_gb"] = mem.used / (1024**3)
        info["memory_total_gb"] = mem.total / (1024**3)
    except Exception:
        pass
    
    return info


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="Path to config.json")
    ap.add_argument("--camera", type=int, default=None, help="Override camera index from config")
    ap.add_argument("--provider", default=None, help='Override provider, e.g. "CUDAExecutionProvider"')
    args = ap.parse_args()

    cfg = load_config(args.config)
    if args.camera is not None:
        cfg.camera_index = int(args.camera)

    def open_camera(index: int) -> cv2.VideoCapture:
        c = cv2.VideoCapture(int(index))
        if not c.isOpened():
            raise RuntimeError(f"Cannot open camera {index}")
        c.set(cv2.CAP_PROP_FRAME_WIDTH, float(cfg.width))
        c.set(cv2.CAP_PROP_FRAME_HEIGHT, float(cfg.height))
        return c

    try:
        cap = open_camera(cfg.camera_index)
    except RuntimeError as e:
        print(f"Camera error: {e}")
        # Try to find available cameras
        for i in range(3):
            test_cap = cv2.VideoCapture(i)
            if test_cap.isOpened():
                test_cap.release()
                print(f"Found available camera at index {i}")
                cfg.camera_index = i
                cap = open_camera(i)
                break
        else:
            print("No cameras found!")
            return

    provider_to_use = args.provider or getattr(cfg, "provider", "auto")
    engine = InsightFaceEngine(provider=provider_to_use)
    recog = FaceRecognizer(cfg.model_dir, threshold=cfg.threshold, unknown_label=cfg.unknown_label)

    simulate_prod = False
    last_send_t = 0.0

    fps_t0 = time.time()
    fps_frames = 0
    fps = 0.0
    
    # Performance tracking
    inference_times = []
    max_inference_samples = 30

    # --- Modern Tk UI ---
    root = tk.Tk()
    root.title("Face Recognition Debug Console")
    root.geometry("1400x800")
    root.minsize(1200, 700)
    root.configure(bg="#0f172a")

    # Custom style
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configure colors
    bg_dark = "#0f172a"
    bg_card = "#1e293b"
    bg_input = "#334155"
    fg_primary = "#e5e7eb"
    fg_secondary = "#94a3b8"
    accent_blue = "#3b82f6"
    accent_green = "#10b981"
    
    style.configure("TFrame", background=bg_dark)
    style.configure("Card.TFrame", background=bg_card, relief="flat")
    style.configure("TLabel", background=bg_dark, foreground=fg_primary, font=("Segoe UI", 10))
    style.configure("Title.TLabel", background=bg_dark, foreground=fg_primary, font=("Segoe UI", 14, "bold"))
    style.configure("Subtitle.TLabel", background=bg_dark, foreground=fg_secondary, font=("Segoe UI", 9))
    style.configure("Card.TLabel", background=bg_card, foreground=fg_primary, font=("Segoe UI", 10))
    style.configure("CardTitle.TLabel", background=bg_card, foreground=fg_primary, font=("Segoe UI", 11, "bold"))
    style.configure("Metric.TLabel", background=bg_card, foreground=accent_blue, font=("Segoe UI", 20, "bold"))
    style.configure("MetricLabel.TLabel", background=bg_card, foreground=fg_secondary, font=("Segoe UI", 9))
    
    style.configure("TButton", background=accent_blue, foreground="white", borderwidth=0, 
                   font=("Segoe UI", 10), padding=8)
    style.map("TButton", background=[("active", "#2563eb")])
    
    style.configure("Success.TButton", background=accent_green, foreground="white")
    style.map("Success.TButton", background=[("active", "#059669")])
    
    style.configure("TCheckbutton", background=bg_card, foreground=fg_primary, font=("Segoe UI", 10))
    style.configure("TScale", background=bg_card, troughcolor=bg_input)

    # Variables
    thresh_var = tk.DoubleVar(value=cfg.threshold)
    minface_var = tk.IntVar(value=cfg.min_face_size)
    maxfaces_var = tk.IntVar(value=getattr(cfg, "max_faces", 20))
    send_interval_var = tk.IntVar(value=cfg.send_interval_ms)
    send_image_var = tk.BooleanVar(value=cfg.send_image)
    simulate_var = tk.BooleanVar(value=simulate_prod)
    cam_var = tk.IntVar(value=cfg.camera_index)
    resize_max_var = tk.IntVar(value=cfg.resize_max)
    running_var = tk.BooleanVar(value=True)
    
    # Label variables for dynamic updates
    thresh_label_text = tk.StringVar(value=f"Recognition Threshold: {cfg.threshold:.2f}")
    minface_label_text = tk.StringVar(value=f"Min Face Size: {cfg.min_face_size}px")
    resize_label_text = tk.StringVar(value=f"Resize Max: {cfg.resize_max} (0=off)")
    maxfaces_label_text = tk.StringVar(value=f"Max Faces: {getattr(cfg, 'max_faces', 20)}")
    interval_label_text = tk.StringVar(value=f"Send Interval: {cfg.send_interval_ms}ms")
    
    status_text = tk.StringVar(value="Initializing...")
    fps_text = tk.StringVar(value="0.0")
    total_faces_text = tk.StringVar(value="0")
    known_faces_text = tk.StringVar(value="0")
    unknown_faces_text = tk.StringVar(value="0")
    inference_time_text = tk.StringVar(value="0.0")
    gpu_status_text = tk.StringVar(value="Checking...")
    gpu_util_text = tk.StringVar(value="0%")
    cpu_util_text = tk.StringVar(value="0%")
    ram_util_text = tk.StringVar(value="0%")

    def apply_threshold(*_):
        nonlocal recog
        cfg.threshold = max(0.05, min(0.95, float(thresh_var.get())))
        thresh_label_text.set(f"Recognition Threshold: {cfg.threshold:.2f}")
        recog = FaceRecognizer(cfg.model_dir, threshold=cfg.threshold, unknown_label=cfg.unknown_label)

    def apply_minface(*_):
        cfg.min_face_size = max(10, int(minface_var.get()))
        minface_label_text.set(f"Min Face Size: {cfg.min_face_size}px")

    def apply_maxfaces(*_):
        cfg.max_faces = max(1, int(maxfaces_var.get()))
        maxfaces_label_text.set(f"Max Faces: {cfg.max_faces}")

    def apply_send_interval(*_):
        cfg.send_interval_ms = max(50, int(send_interval_var.get()))
        interval_label_text.set(f"Send Interval: {cfg.send_interval_ms}ms")

    def apply_send_image(*_):
        cfg.send_image = bool(send_image_var.get())

    def apply_simulate(*_):
        nonlocal simulate_prod
        simulate_prod = bool(simulate_var.get())

    def apply_camera(*_):
        nonlocal cap
        new_idx = int(cam_var.get())
        test_cap = open_camera(new_idx)
        if test_cap is not None and test_cap.isOpened():
            try:
                cap.release()
            except Exception:
                pass
            cap = test_cap
            cfg.camera_index = new_idx
            status_text.set(f"✓ Switched to camera {new_idx}")
        else:
            cam_var.set(cfg.camera_index)
            status_text.set(f"✗ Camera {new_idx} not available")

    def apply_resize_max(*_):
        cfg.resize_max = max(0, int(resize_max_var.get()))
        resize_label_text.set(f"Resize Max: {cfg.resize_max} (0=off)")

    def on_save():
        save_config(cfg, args.config)
        status_text.set(f"✓ Configuration saved")

    def on_exit():
        running_var.set(False)
        try:
            cap.release()
        except Exception:
            pass
        root.destroy()

    def on_toggle_run():
        running_var.set(not running_var.get())
        status_text.set("▶ Running" if running_var.get() else "⏸ Paused")

    # Main container
    main_container = ttk.Frame(root, style="TFrame")
    main_container.pack(fill="both", expand=True, padx=10, pady=10)

    # Header
    header = ttk.Frame(main_container, style="TFrame")
    header.pack(fill="x", pady=(0, 10))
    
    ttk.Label(header, text="🎯 Face Recognition Debug Console", style="Title.TLabel").pack(side="left")
    
    providers_info = ", ".join(get_available_providers())
    ttk.Label(header, text=f"Providers: {providers_info}", style="Subtitle.TLabel").pack(side="left", padx=(20, 0))

    # Content area - 3 columns
    content = ttk.Frame(main_container, style="TFrame")
    content.pack(fill="both", expand=True)

    # Left panel - Controls
    left_panel = ttk.Frame(content, style="Card.TFrame", width=320)
    left_panel.pack(side="left", fill="y", padx=(0, 10))
    left_panel.pack_propagate(False)

    # Middle panel - Video
    middle_panel = ttk.Frame(content, style="TFrame")
    middle_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

    # Right panel - Stats
    right_panel = ttk.Frame(content, style="Card.TFrame", width=280)
    right_panel.pack(side="right", fill="y")
    right_panel.pack_propagate(False)

    # === LEFT PANEL - CONTROLS ===
    left_scroll = tk.Canvas(left_panel, bg=bg_card, highlightthickness=0)
    left_scroll.pack(side="left", fill="both", expand=True)
    
    scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=left_scroll.yview)
    scrollbar.pack(side="right", fill="y")
    left_scroll.configure(yscrollcommand=scrollbar.set)
    
    controls_frame = ttk.Frame(left_scroll, style="Card.TFrame")
    left_scroll.create_window((0, 0), window=controls_frame, anchor="nw")
    
    def configure_scroll(event):
        left_scroll.configure(scrollregion=left_scroll.bbox("all"))
    controls_frame.bind("<Configure>", configure_scroll)

    # Controls content
    ttk.Label(controls_frame, text="⚙️ Settings", style="CardTitle.TLabel").pack(anchor="w", padx=15, pady=(15, 10))

    # Threshold
    ttk.Label(controls_frame, textvariable=thresh_label_text, style="Card.TLabel").pack(fill="x", padx=15, pady=(10, 2))
    thresh_scale = ttk.Scale(controls_frame, from_=0.05, to=0.95, orient="horizontal", variable=thresh_var, 
                            command=lambda v: apply_threshold())
    thresh_scale.pack(fill="x", padx=15)
    
    # Min face size
    ttk.Label(controls_frame, textvariable=minface_label_text, style="Card.TLabel").pack(fill="x", padx=15, pady=(10, 2))
    minface_scale = ttk.Scale(controls_frame, from_=10, to=400, orient="horizontal", variable=minface_var,
                             command=lambda v: apply_minface())
    minface_scale.pack(fill="x", padx=15)

    # Max faces (New)
    ttk.Label(controls_frame, textvariable=maxfaces_label_text, style="Card.TLabel").pack(fill="x", padx=15, pady=(10, 2))
    maxfaces_scale = ttk.Scale(controls_frame, from_=1, to=50, orient="horizontal", variable=maxfaces_var,
                             command=lambda v: apply_maxfaces())
    maxfaces_scale.pack(fill="x", padx=15)

    # Resize max
    ttk.Label(controls_frame, textvariable=resize_label_text, style="Card.TLabel").pack(fill="x", padx=15, pady=(10, 2))
    resize_scale = ttk.Scale(controls_frame, from_=0, to=1920, orient="horizontal", variable=resize_max_var,
                            command=lambda v: apply_resize_max())
    resize_scale.pack(fill="x", padx=15)

    # Send interval
    ttk.Label(controls_frame, textvariable=interval_label_text, style="Card.TLabel").pack(fill="x", padx=15, pady=(10, 2))
    interval_scale = ttk.Scale(controls_frame, from_=50, to=2000, orient="horizontal", variable=send_interval_var,
                              command=lambda v: apply_send_interval())
    interval_scale.pack(fill="x", padx=15)

    # Camera index
    cam_frame = ttk.Frame(controls_frame, style="Card.TFrame")
    cam_frame.pack(fill="x", padx=15, pady=(10, 0))
    ttk.Label(cam_frame, text="Camera Index:", style="Card.TLabel").pack(side="left")
    cam_spin = ttk.Spinbox(cam_frame, from_=0, to=10, textvariable=cam_var, command=apply_camera, width=8)
    cam_spin.pack(side="left", padx=(10, 0))

    # Checkboxes
    ttk.Checkbutton(controls_frame, text="📤 Send image (base64)", variable=send_image_var, 
                   command=apply_send_image, style="TCheckbutton").pack(anchor="w", padx=15, pady=(15, 5))
    ttk.Checkbutton(controls_frame, text="🚀 Simulate production mode", variable=simulate_var,
                   command=apply_simulate, style="TCheckbutton").pack(anchor="w", padx=15, pady=5)

    # Buttons
    ttk.Label(controls_frame, text="", style="Card.TLabel").pack(pady=10)  # Spacer
    
    btn_frame = ttk.Frame(controls_frame, style="Card.TFrame")
    btn_frame.pack(fill="x", padx=15, pady=5)
    ttk.Button(btn_frame, text="▶ Start/Pause", command=on_toggle_run).pack(fill="x", pady=2)
    ttk.Button(btn_frame, text="💾 Save Config", command=on_save, style="Success.TButton").pack(fill="x", pady=2)
    ttk.Button(btn_frame, text="❌ Exit", command=on_exit).pack(fill="x", pady=2)

    # Status
    ttk.Label(controls_frame, text="", style="Card.TLabel").pack(pady=5)  # Spacer
    ttk.Label(controls_frame, text="Status:", style="CardTitle.TLabel").pack(anchor="w", padx=15)
    status_label = ttk.Label(controls_frame, textvariable=status_text, wraplength=280, style="Card.TLabel")
    status_label.pack(anchor="w", padx=15, pady=5)

    # === MIDDLE PANEL - VIDEO ===
    video_card = ttk.Frame(middle_panel, style="Card.TFrame")
    video_card.pack(fill="both", expand=True)
    
    ttk.Label(video_card, text="📹 Live Video Feed", style="CardTitle.TLabel").pack(anchor="w", padx=15, pady=(15, 10))
    
    image_label = ttk.Label(video_card, background=bg_input)
    image_label.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    image_label.imgtk = None

    # === RIGHT PANEL - STATS ===
    stats_container = ttk.Frame(right_panel, style="Card.TFrame")
    stats_container.pack(fill="both", expand=True, padx=10, pady=10)

    ttk.Label(stats_container, text="📊 Performance", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 15))

    # FPS
    fps_card = ttk.Frame(stats_container, style="Card.TFrame")
    fps_card.pack(fill="x", pady=5)
    ttk.Label(fps_card, text="FPS", style="MetricLabel.TLabel").pack(anchor="w")
    ttk.Label(fps_card, textvariable=fps_text, style="Metric.TLabel").pack(anchor="w")

    # Inference time
    inf_card = ttk.Frame(stats_container, style="Card.TFrame")
    inf_card.pack(fill="x", pady=5)
    ttk.Label(inf_card, text="Inference (ms)", style="MetricLabel.TLabel").pack(anchor="w")
    ttk.Label(inf_card, textvariable=inference_time_text, style="Metric.TLabel").pack(anchor="w")

    ttk.Label(stats_container, text="", style="Card.TLabel").pack(pady=5)  # Spacer
    ttk.Label(stats_container, text="👤 Faces Detected", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 10))

    # Total faces
    total_card = ttk.Frame(stats_container, style="Card.TFrame")
    total_card.pack(fill="x", pady=5)
    ttk.Label(total_card, text="Total", style="MetricLabel.TLabel").pack(anchor="w")
    ttk.Label(total_card, textvariable=total_faces_text, style="Metric.TLabel").pack(anchor="w")

    # Known faces
    known_card = ttk.Frame(stats_container, style="Card.TFrame")
    known_card.pack(fill="x", pady=5)
    ttk.Label(known_card, text="Known", style="MetricLabel.TLabel").pack(anchor="w")
    ttk.Label(known_card, textvariable=known_faces_text, style="Metric.TLabel").pack(anchor="w")

    # Unknown faces
    unknown_card = ttk.Frame(stats_container, style="Card.TFrame")
    unknown_card.pack(fill="x", pady=5)
    ttk.Label(unknown_card, text="Unknown", style="MetricLabel.TLabel").pack(anchor="w")
    ttk.Label(unknown_card, textvariable=unknown_faces_text, style="Metric.TLabel").pack(anchor="w")

    ttk.Label(stats_container, text="", style="Card.TLabel").pack(pady=5)  # Spacer
    ttk.Label(stats_container, text="💻 System", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 10))

    # GPU Status
    gpu_card = ttk.Frame(stats_container, style="Card.TFrame")
    gpu_card.pack(fill="x", pady=5)
    ttk.Label(gpu_card, text="GPU", style="MetricLabel.TLabel").pack(anchor="w")
    ttk.Label(gpu_card, textvariable=gpu_status_text, style="Card.TLabel", wraplength=240).pack(anchor="w")
    ttk.Label(gpu_card, textvariable=gpu_util_text, style="Card.TLabel").pack(anchor="w")

    # CPU
    cpu_card = ttk.Frame(stats_container, style="Card.TFrame")
    cpu_card.pack(fill="x", pady=5)
    ttk.Label(cpu_card, text="CPU Usage", style="MetricLabel.TLabel").pack(anchor="w")
    ttk.Label(cpu_card, textvariable=cpu_util_text, style="Card.TLabel").pack(anchor="w")

    # RAM
    ram_card = ttk.Frame(stats_container, style="Card.TFrame")
    ram_card.pack(fill="x", pady=5)
    ttk.Label(ram_card, text="RAM Usage", style="MetricLabel.TLabel").pack(anchor="w")
    ttk.Label(ram_card, textvariable=ram_util_text, style="Card.TLabel").pack(anchor="w")

    # Update system info periodically
    def update_system_info():
        # GPU info
        gpu_info = get_gpu_info()
        if gpu_info["available"]:
            gpu_status_text.set(f"✓ {gpu_info['name'][:25]}")
            gpu_util_text.set(f"Utilization: {gpu_info['utilization']:.1f}% | "
                            f"Memory: {gpu_info['memory_used']:.0f}/{gpu_info['memory_total']:.0f} MB")
        else:
            if is_gpu_available():
                gpu_status_text.set("✓ CUDA Available")
                gpu_util_text.set("(Install GPUtil for monitoring)")
            else:
                gpu_status_text.set("⚠ CPU Mode")
                gpu_util_text.set("No CUDA detected")
        
        # CPU/RAM info
        sys_info = get_cpu_memory_info()
        cpu_util_text.set(f"{sys_info['cpu_percent']:.1f}%")
        ram_util_text.set(f"{sys_info['memory_percent']:.1f}% "
                         f"({sys_info['memory_used_gb']:.1f}/{sys_info['memory_total_gb']:.1f} GB)")
        
        root.after(2000, update_system_info)  # Update every 2 seconds

    def update_frame() -> None:
        nonlocal last_send_t, fps_t0, fps_frames, fps, recog, inference_times

        if not running_var.get():
            root.after(30, update_frame)
            return

        ok, frame = cap.read()
        if not ok or frame is None:
            status_text.set("⚠ Camera read failed")
            root.after(30, update_frame)
            return

        # Measure inference time
        t_start = time.time()
        
        disp, _scale = resize_max_side(frame, cfg.resize_max)
        
        # Limit max faces to prevent lag
        limit_faces = getattr(cfg, "max_faces", 20)
        dets = engine.detect_and_embed(disp, min_face_size=cfg.min_face_size, max_faces=limit_faces)

        known_faces: List[Dict[str, Any]] = []
        unknown_count = 0

        # Draw & classify
        for d in dets:
            rr = recog.recognize(d.embedding)
            x1, y1, x2, y2 = d.bbox_xyxy
            draw_face_box(disp, x1, y1, x2, y2, rr.name, rr.confidence, rr.known)
            if rr.known:
                known_faces.append({"name": rr.name, "confidence": float(rr.confidence)})
            else:
                unknown_count += 1

        t_end = time.time()
        inference_time_ms = (t_end - t_start) * 1000
        inference_times.append(inference_time_ms)
        if len(inference_times) > max_inference_samples:
            inference_times.pop(0)
        
        avg_inference = sum(inference_times) / len(inference_times) if inference_times else 0

        total_faces = len(dets)

        # Update stats
        total_faces_text.set(str(total_faces))
        known_faces_text.set(str(len(known_faces)))
        unknown_faces_text.set(str(unknown_count))
        inference_time_text.set(f"{avg_inference:.1f}")

        # FPS calc
        fps_frames += 1
        dt = time.time() - fps_t0
        if dt >= 1.0:
            fps = fps_frames / dt
            fps_frames = 0
            fps_t0 = time.time()
            fps_text.set(f"{fps:.1f}")

        # Simulate production sending
        if simulate_prod:
            now_t = time.time()
            if (now_t - last_send_t) * 1000.0 >= float(cfg.send_interval_ms):
                last_send_t = now_t
                img_b64 = bgr_to_jpeg_base64(disp, quality=cfg.jpeg_quality) if cfg.send_image else None
                payload = {
                    "timestamp": now_iso(),
                    "camera_id": cfg.camera_id,
                    "total_faces": total_faces,
                    "known_faces": known_faces,
                    "unknown_faces": unknown_count,
                    "stream_image": img_b64,
                }
                send_http(cfg.endpoint_http, payload)

        # Render to Tk
        rgb = cv2.cvtColor(disp, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)

        # Fit to panel
        panel_width = max(400, image_label.winfo_width() - 20)
        panel_height = max(300, image_label.winfo_height() - 20)
        iw, ih = img.size
        scale = min(panel_width / iw, panel_height / ih) if iw > 0 and ih > 0 else 1
        new_size = (int(iw * scale), int(ih * scale))
        if new_size[0] > 0 and new_size[1] > 0:
            img = img.resize(new_size, Image.BILINEAR)

        imgtk = ImageTk.PhotoImage(image=img)
        image_label.imgtk = imgtk
        image_label.configure(image=imgtk)

        # Schedule next frame
        root.after(1, update_frame)

    root.protocol("WM_DELETE_WINDOW", on_exit)
    status_text.set("▶ Running")
    root.after(100, update_frame)
    root.after(500, update_system_info)
    root.mainloop()


if __name__ == "__main__":
    main()
