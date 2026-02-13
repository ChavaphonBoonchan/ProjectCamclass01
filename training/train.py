from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from tqdm import tqdm

from face_common.face_engine import InsightFaceEngine


def iter_images(dataset_dir: Path) -> List[Tuple[Path, str]]:
    items: List[Tuple[Path, str]] = []
    for person_dir in sorted([p for p in dataset_dir.iterdir() if p.is_dir()]):
        label = person_dir.name
        for ext in ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"):
            for img_path in person_dir.glob(ext):
                items.append((img_path, label))
    return items


def build_label_map(labels: List[str]) -> Tuple[Dict[str, int], Dict[int, str]]:
    uniq = sorted(set(labels))
    name_to_id = {name: i for i, name in enumerate(uniq)}
    id_to_name = {i: name for name, i in name_to_id.items()}
    return name_to_id, id_to_name


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True, help="Path to dataset/ folder")
    ap.add_argument("--output", required=True, help="Output folder for model_store")
    ap.add_argument("--classifier", default="svm", choices=["svm", "none"], help="svm or none")
    ap.add_argument("--min-face-size", type=int, default=40)
    ap.add_argument("--max-faces-per-image", type=int, default=1, help="0=unlimited")
    ap.add_argument("--provider", default="CPUExecutionProvider")
    args = ap.parse_args()

    dataset_dir = Path(args.dataset)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    items = iter_images(dataset_dir)
    if not items:
        raise SystemExit(f"No images found under {dataset_dir}")

    labels = [lbl for _, lbl in items if lbl.lower() != "unknown"]
    name_to_id, id_to_name = build_label_map(labels)

    engine = InsightFaceEngine(provider=args.provider)

    X: List[np.ndarray] = []
    y: List[int] = []

    # Process images
    for img_path, label in tqdm(items, desc="Extract embeddings"):
        if label.lower() == "unknown":
            continue
        import cv2

        img = cv2.imread(str(img_path))
        if img is None:
            continue
        faces = engine.detect_and_embed(
            img, min_face_size=args.min_face_size, max_faces=args.max_faces_per_image
        )
        if not faces:
            continue
        # take largest face (by bbox area)
        faces.sort(key=lambda f: (f.bbox_xyxy[2] - f.bbox_xyxy[0]) * (f.bbox_xyxy[3] - f.bbox_xyxy[1]), reverse=True)
        emb = faces[0].embedding
        X.append(emb)
        y.append(name_to_id[label])

    if not X:
        raise SystemExit("No embeddings extracted. Check your dataset quality / min-face-size.")

    Xn = np.stack(X).astype(np.float32)
    yn = np.asarray(y, dtype=np.int64)

    # Save gallery for cosine fallback
    np.save(out_dir / "embeddings.npy", Xn)
    np.save(out_dir / "labels.npy", yn)
    (out_dir / "label_map.json").write_text(
        json.dumps({str(k): v for k, v in id_to_name.items()}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    if args.classifier == "svm":
        from sklearn.svm import SVC
        import joblib

        clf = SVC(kernel="linear", probability=True)
        clf.fit(Xn, yn)
        joblib.dump(clf, out_dir / "model.pkl")
        print(f"Saved SVM classifier -> {out_dir / 'model.pkl'}")
    else:
        print("Classifier disabled (cosine-only).")

    print("Saved:")
    print(f"- embeddings.npy, labels.npy -> {out_dir}")
    print(f"- label_map.json -> {out_dir}")


if __name__ == "__main__":
    main()

