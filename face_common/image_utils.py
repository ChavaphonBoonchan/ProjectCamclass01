from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Tuple

import cv2
import numpy as np


@dataclass
class DrawStyle:
    box_color: Tuple[int, int, int] = (0, 255, 0)
    unknown_color: Tuple[int, int, int] = (0, 0, 255)
    thickness: int = 2


def resize_max_side(img_bgr: np.ndarray, max_side: int) -> tuple[np.ndarray, float]:
    if max_side <= 0:
        return img_bgr, 1.0
    h, w = img_bgr.shape[:2]
    long_side = max(h, w)
    if long_side <= max_side:
        return img_bgr, 1.0
    scale = max_side / float(long_side)
    new_w = int(round(w * scale))
    new_h = int(round(h * scale))
    resized = cv2.resize(img_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return resized, scale


def bgr_to_jpeg_base64(img_bgr: np.ndarray, quality: int = 75) -> str:
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), int(quality)]
    ok, buf = cv2.imencode(".jpg", img_bgr, encode_param)
    if not ok:
        return ""
    return base64.b64encode(buf.tobytes()).decode("ascii")


def draw_face_box(
    img_bgr: np.ndarray,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    label: str,
    conf: float,
    known: bool,
    style: DrawStyle = DrawStyle(),
) -> None:
    color = style.box_color if known else style.unknown_color
    cv2.rectangle(img_bgr, (x1, y1), (x2, y2), color, style.thickness)
    text = f"{label} {conf:.2f}"
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
    cv2.rectangle(img_bgr, (x1, y1 - th - 8), (x1 + tw + 6, y1), color, -1)
    cv2.putText(
        img_bgr,
        text,
        (x1 + 3, y1 - 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 0, 0),
        2,
        cv2.LINE_AA,
    )

