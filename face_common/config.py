from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path
from typing import Any, Optional


@dataclass
class DetectionConfig:
    # Camera / input
    camera_index: int = 0
    camera_id: str = "cam01"
    width: int = 1280
    height: int = 720
    fps_limit: int = 0  # 0 = unlimited

    # Model paths
    model_dir: str = "model_store"  # expects model.pkl, label_map.json

    # Inference provider: "auto" (auto-detect), "CPUExecutionProvider" or "CUDAExecutionProvider" (if onnxruntime-gpu installed)
    provider: str = "auto"

    # Recognition tuning
    threshold: float = 0.45  # lower = stricter for cosine, depends on embeddings
    unknown_label: str = "unknown"
    min_face_size: int = 40
    max_faces: int = 20

    # Sending
    send_mode: str = "http"  # "http" or "ws"
    endpoint_http: str = "http://127.0.0.1:8000/api/v1/ingest"
    endpoint_ws: str = "ws://127.0.0.1:8000/ws"
    send_interval_ms: int = 250
    send_image: bool = True
    jpeg_quality: int = 75

    # Performance
    resize_max: int = 960  # resize longer side to this for faster inference (0=disable)


def load_config(path: str | Path) -> DetectionConfig:
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    return DetectionConfig(**data)


def save_config(cfg: DetectionConfig, path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(asdict(cfg), ensure_ascii=False, indent=2), encoding="utf-8")


def get_optional(d: dict[str, Any], key: str, default: Optional[Any] = None) -> Any:
    return d.get(key, default)

