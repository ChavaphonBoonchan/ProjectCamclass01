from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np


@dataclass
class FaceDetection:
    bbox_xyxy: Tuple[int, int, int, int]
    det_score: float
    embedding: np.ndarray  # shape (d,)


def get_available_providers() -> List[str]:
    """
    TH: ตรวจสอบ providers ที่ใช้ได้ใน ONNXRuntime
    EN: Check available providers in ONNXRuntime
    """
    try:
        import onnxruntime as ort
        return ort.get_available_providers()
    except Exception:
        return ["CPUExecutionProvider"]


def auto_select_provider(preferred: Optional[str] = None) -> str:
    """
    TH: เลือก provider อัตโนมัติ โดยลำดับความสำคัญ: CUDA > CPU
    EN: Auto-select provider with priority: CUDA > CPU
    """
    available = get_available_providers()
    print(f"[InsightFace] Available providers: {available}")
    
    # If user specifies a preferred provider
    if preferred:
        if preferred in available:
            print(f"[InsightFace] Force using provider: {preferred}")
            return preferred
        else:
            print(f"[InsightFace] WARNING: Forced provider '{preferred}' not found in {available}")
            print(f"[InsightFace] Falling back to auto-selection...")
    
    # Priority order: CUDA > CPU
    priority = ["CUDAExecutionProvider", "CPUExecutionProvider"]
    for prov in priority:
        if prov in available:
            return prov
    
    # Fallback
    return "CPUExecutionProvider"


def is_gpu_available() -> bool:
    """
    TH: ตรวจสอบว่ามี GPU (CUDA) ใช้งานได้หรือไม่
    EN: Check if GPU (CUDA) is available
    """
    return "CUDAExecutionProvider" in get_available_providers()


class InsightFaceEngine:
    """
    TH: Wrapper รอบ InsightFace สำหรับ detect + embedding ในขั้นตอนเดียว
    EN: Thin wrapper around InsightFace FaceAnalysis for detection+embedding.
    """

    def __init__(
        self,
        provider: str = "auto",
        det_size: Tuple[int, int] = (640, 640),
    ) -> None:
        from insightface.app import FaceAnalysis

        # Auto-select provider if "auto" is specified
        if provider == "auto":
            provider = auto_select_provider()
        else:
            provider = auto_select_provider(preferred=provider)
        
        self.provider = provider
        print(f"[InsightFace] Using provider: {provider}")
        
        self.app = FaceAnalysis(
            name="buffalo_l",
            providers=[provider],
        )
        self.app.prepare(ctx_id=0, det_size=det_size)
        
        # Verify provider
        try:
            # Check the detection model's provider
            det_providers = self.app.det_model.session.get_providers()
            print(f"[InsightFace] Detection Model is running on: {det_providers[0]}")
            
            # Check the recognition model's provider (if loaded)
            if hasattr(self.app, 'rec_model') and self.app.rec_model:
                 rec_providers = self.app.rec_model.session.get_providers()
                 print(f"[InsightFace] Recognition Model is running on: {rec_providers[0]}")
        except Exception as e:
            print(f"[InsightFace] Could not verify active provider: {e}")

    def detect_and_embed(
        self,
        img_bgr: np.ndarray,
        min_face_size: int = 40,
        max_faces: int = 0,
    ) -> List[FaceDetection]:
        faces = self.app.get(img_bgr)
        out: List[FaceDetection] = []
        for f in faces:
            x1, y1, x2, y2 = [int(v) for v in f.bbox]
            w = x2 - x1
            h = y2 - y1
            if min(w, h) < int(min_face_size):
                continue
            emb = np.asarray(f.embedding, dtype=np.float32)
            norm = np.linalg.norm(emb) + 1e-12
            emb = emb / norm
            out.append(
                FaceDetection(
                    bbox_xyxy=(x1, y1, x2, y2),
                    det_score=float(getattr(f, "det_score", 1.0)),
                    embedding=emb,
                )
            )
            if max_faces and len(out) >= max_faces:
                break
        return out

