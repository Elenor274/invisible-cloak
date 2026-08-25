"""Create an invisibility-cloak effect with a webcam and a red cloth."""

from __future__ import annotations

import argparse
import time

import cv2
import numpy as np

LOWER_RED_1 = np.array([0, 120, 70])
UPPER_RED_1 = np.array([10, 255, 255])
LOWER_RED_2 = np.array([170, 120, 70])
UPPER_RED_2 = np.array([180, 255, 255])


def build_red_mask(frame: np.ndarray) -> np.ndarray:
    """Return a denoised mask covering red regions in a BGR frame."""
    if frame.size == 0:
        raise ValueError("Frame must not be empty.")

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_RED_1, UPPER_RED_1)
    mask |= cv2.inRange(hsv, LOWER_RED_2, UPPER_RED_2)

    kernel = np.ones((3, 3), dtype=np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=1)
    return cv2.GaussianBlur(mask, (7, 7), 0)


def capture_background(
    camera: cv2.VideoCapture,
    *,
    frame_count: int,
) -> np.ndarray:
    """Capture several frames and combine them into a stable background."""
    frames: list[np.ndarray] = []
    for _ in range(frame_count):
        success, frame = camera.read()
        if success:
            frames.append(cv2.flip(frame, 1))

    if not frames:
        raise RuntimeError("The camera did not return any frames.")

    return np.median(np.stack(frames), axis=0).astype(np.uint8)


def apply_cloak_effect(
    frame: np.ndarray,
    background: np.ndarray,
) -> np.ndarray:
    """Replace red pixels in a frame with pixels from the background."""
    mask = build_red_mask(frame)
    foreground = cv2.bitwise_and(frame, frame, mask=cv2.bitwise_not(mask))
    hidden_region = cv2.bitwise_and(background, background, mask=mask)
    return cv2.add(foreground, hidden_region)


def run(
    *,
    camera_index: int = 0,
    warmup_seconds: float = 3.0,
    background_frames: int = 40,
) -> None:
    """Start the interactive webcam application."""
    camera = cv2.VideoCapture(camera_index)
    if not camera.isOpened():
        raise RuntimeError(f"Could not open camera {camera_index}.")

    try:
        print(f"Warming up camera for {warmup_seconds:g} seconds...")
        time.sleep(warmup_seconds)
        print("Move out of frame while the background is captured.")
        background = capture_background(camera, frame_count=background_frames)
        print("Ready. Hold up a red cloth; press Q to quit.")

        while True:
            success, frame = camera.read()
            if not success:
                break

            frame = cv2.flip(frame, 1)
            result = apply_cloak_effect(frame, background)
            cv2.imshow("Invisible Cloak", result)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", type=int, default=0, help="Camera device index")
    parser.add_argument("--warmup", type=float, default=3.0, help="Warm-up seconds")
    parser.add_argument(
        "--background-frames",
        type=int,
        default=40,
        help="Frames used to estimate the background",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    run(
        camera_index=arguments.camera,
        warmup_seconds=arguments.warmup,
        background_frames=arguments.background_frames,
    )
