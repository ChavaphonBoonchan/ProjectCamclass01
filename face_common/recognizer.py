from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import joblib
import numpy as np


@dataclass
class RecognitionResult:
    name: str
    confidence: float
    known: bool


class FaceRecognizer:
    """
    TH: Recognizer ที่รองรับ 2 โหมด
    - classifier (เช่น SVM) ถ้ามี model.pkl
    - cosine similarity fallback จาก embeddings.npy (ถ้าไม่มี classifier)

    EN: Recognizer supports classifier + cosine fallback.
    """

    def __init__(
        self,
        model_dir: str | Path,
        threshold: float = 0.45,
        unknown_label: str = "unknown",
    ) -> None:
        self.model_dir = Path(model_dir)
        self.threshold = float(threshold)
        self.unknown_label = unknown_label

        self.label_map: Dict[int, str] = {}
        self.clf = None
        self.gallery_emb: Optional[np.ndarray] = None
        self.gallery_labels: Optional[np.ndarray] = None

        self._load()

    def _load(self) -> None:
        label_map_path = self.model_dir / "label_map.json"
        if label_map_path.exists():
            data = json.loads(label_map_path.read_text(encoding="utf-8"))
            self.label_map = {int(k): str(v) for k, v in data.items()}

        model_path = self.model_dir / "model.pkl"
        if model_path.exists():
            self.clf = joblib.load(model_path)

        emb_path = self.model_dir / "embeddings.npy"
        labels_path = self.model_dir / "labels.npy"
        if emb_path.exists() and labels_path.exists():
            self.gallery_emb = np.load(emb_path).astype(np.float32)
            self.gallery_labels = np.load(labels_path).astype(np.int64)

            # normalize
            norms = np.linalg.norm(self.gallery_emb, axis=1, keepdims=True) + 1e-12
            self.gallery_emb = self.gallery_emb / norms

    def _predict_cosine(self, emb: np.ndarray) -> RecognitionResult:
        if self.gallery_emb is None or self.gallery_labels is None or len(self.gallery_emb) == 0:
            return RecognitionResult(name=self.unknown_label, confidence=0.0, known=False)

        sims = self.gallery_emb @ emb.reshape(-1, 1)
        sims = sims.reshape(-1)
        best_i = int(np.argmax(sims))
        best_sim = float(sims[best_i])  # cosine similarity in [-1, 1], higher = more similar
        label_id = int(self.gallery_labels[best_i])
        name = self.label_map.get(label_id, str(label_id))
        # TH: ถ้า similarity ต่ำกว่า threshold ให้ถือว่า "ไม่ใช่คนในโมเดล" -> unknown
        # EN: If similarity < threshold, treat as unknown (not in model).
        known = best_sim >= self.threshold
        if not known:
            return RecognitionResult(name=self.unknown_label, confidence=best_sim, known=False)
        return RecognitionResult(name=name, confidence=best_sim, known=True)

    def _predict_classifier(self, emb: np.ndarray) -> RecognitionResult:
        # For SVM with probability=True, use predict_proba if available
        if self.clf is None:
            return self._predict_cosine(emb)

        if hasattr(self.clf, "predict_proba"):
            probs = self.clf.predict_proba(emb.reshape(1, -1))[0]
            best_i = int(np.argmax(probs))
            conf = float(probs[best_i])
            class_id = int(getattr(self.clf, "classes_", [best_i])[best_i])
            name = self.label_map.get(class_id, str(class_id))
            # TH: ใช้ probability เป็นความมั่นใจ ถ้าต่ำกว่า threshold -> unknown
            # EN: Use probability as confidence; if below threshold => unknown.
            known = conf >= self.threshold
            if not known:
                return RecognitionResult(name=self.unknown_label, confidence=conf, known=False)
            return RecognitionResult(name=name, confidence=conf, known=True)

        pred = int(self.clf.predict(emb.reshape(1, -1))[0])
        name = self.label_map.get(pred, str(pred))
        # No probability, approximate using cosine as confidence if gallery exists
        rr = self._predict_cosine(emb)
        if rr.known:
            return RecognitionResult(name=name, confidence=rr.confidence, known=True)
        return RecognitionResult(name=self.unknown_label, confidence=rr.confidence, known=False)

    def recognize(self, embedding: np.ndarray) -> RecognitionResult:
        emb = np.asarray(embedding, dtype=np.float32)
        n = np.linalg.norm(emb) + 1e-12
        emb = emb / n
        return self._predict_classifier(emb)

