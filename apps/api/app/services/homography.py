"""
Homography computation for court calibration.

Converts image pixel coordinates to real-world court coordinates using
a perspective transform (homography matrix) computed from at least 4
matching point pairs.

No OpenCV required for this computation — we use numpy directly to solve
the Direct Linear Transform (DLT) system, keeping the dependency minimal.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import numpy as np
from numpy.typing import NDArray

logger = logging.getLogger(__name__)

# ── NBA full court reference points (feet, origin at top-left corner) ──────────
# 9 standard calibration points on the court.  Keys are stable identifiers
# surfaced to the frontend CalibrationCanvas.
REFERENCE_POINTS: dict[str, tuple[float, float]] = {
    "court_tl": (0.0, 0.0),         # top-left corner
    "court_tr": (94.0, 0.0),         # top-right corner
    "court_bl": (0.0, 50.0),         # bottom-left corner
    "court_br": (94.0, 50.0),        # bottom-right corner
    "center": (47.0, 25.0),          # centre circle
    "left_ft": (19.0, 25.0),         # left free-throw line centre
    "right_ft": (75.0, 25.0),        # right free-throw line centre
    "left_basket": (5.25, 25.0),     # left basket
    "right_basket": (88.75, 25.0),   # right basket
}


class CalibrationError(ValueError):
    """Raised when calibration data is invalid or homography cannot be computed."""


def _build_dlt_row(src: tuple[float, float], dst: tuple[float, float]) -> list[list[float]]:
    """Build two DLT rows for one point correspondence."""
    x, y = src
    u, v = dst
    return [
        [-x, -y, -1, 0, 0, 0, u * x, u * y, u],
        [0, 0, 0, -x, -y, -1, v * x, v * y, v],
    ]


def compute_homography(
    image_points: list[tuple[float, float]],
    court_points: list[tuple[float, float]],
) -> NDArray[np.float64]:
    """
    Compute a 3×3 homography matrix mapping image pixels → court coordinates.

    Uses the normalised DLT algorithm followed by SVD for numerical stability.
    Requires at least 4 non-collinear point pairs.

    Args:
        image_points: [(px, py), …] pixel coordinates from the video frame.
        court_points: [(cx, cy), …] corresponding court coordinates (feet).

    Returns:
        3×3 numpy float64 homography matrix H such that:
          [u, v, 1]^T ≅ H @ [x, y, 1]^T   (homogeneous coordinates)

    Raises:
        CalibrationError: if fewer than 4 points supplied or matrix is singular.
    """
    if len(image_points) != len(court_points):
        raise CalibrationError("image_points and court_points must have the same length.")
    if len(image_points) < 4:
        raise CalibrationError("At least 4 point correspondences are required.")

    rows: list[list[float]] = []
    for img_pt, court_pt in zip(image_points, court_points):
        rows.extend(_build_dlt_row(img_pt, court_pt))

    A = np.array(rows, dtype=np.float64)
    try:
        _, _, Vt = np.linalg.svd(A)
    except np.linalg.LinAlgError as exc:
        raise CalibrationError(f"SVD failed — point configuration may be degenerate: {exc}") from exc

    h = Vt[-1]
    H = h.reshape(3, 3)
    H /= H[2, 2]  # normalise so H[2,2] == 1
    return H


def apply_homography(
    H: NDArray[np.float64],
    pixel_x: float,
    pixel_y: float,
) -> tuple[float, float]:
    """Map a single image pixel to court coordinates using the homography matrix."""
    src = np.array([pixel_x, pixel_y, 1.0], dtype=np.float64)
    dst = H @ src
    if abs(dst[2]) < 1e-10:
        raise CalibrationError("Homogeneous coordinate is zero — point is at infinity.")
    return float(dst[0] / dst[2]), float(dst[1] / dst[2])


def calibration_to_json(
    H: NDArray[np.float64],
    image_points: list[tuple[float, float]],
    court_points: list[tuple[float, float]],
    point_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Serialise calibration result to a JSON-compatible dict for storage."""
    return {
        "schema_version": "1.0",
        "homography_matrix": H.tolist(),
        "image_points": image_points,
        "court_points": court_points,
        "point_ids": point_ids or [],
    }


def calibration_from_json(data: dict[str, Any]) -> NDArray[np.float64]:
    """Deserialise homography matrix from stored calibration_json."""
    try:
        return np.array(data["homography_matrix"], dtype=np.float64)
    except (KeyError, ValueError) as exc:
        raise CalibrationError(f"Invalid calibration_json: {exc}") from exc
