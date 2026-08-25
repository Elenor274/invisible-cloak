import cv2
import numpy as np
import pytest

from invisibility_cloak import apply_cloak_effect, build_red_mask


def test_red_region_is_detected() -> None:
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.rectangle(frame, (30, 30), (70, 70), (0, 0, 255), thickness=-1)

    mask = build_red_mask(frame)

    assert mask[50, 50] > 240
    assert mask[5, 5] == 0


def test_cloak_replaces_red_pixels_with_background() -> None:
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.rectangle(frame, (30, 30), (70, 70), (0, 0, 255), thickness=-1)
    background = np.full_like(frame, fill_value=(255, 0, 0))

    result = apply_cloak_effect(frame, background)

    assert np.array_equal(result[50, 50], background[50, 50])
    assert np.array_equal(result[5, 5], frame[5, 5])


def test_empty_frame_is_rejected() -> None:
    with pytest.raises(ValueError, match="empty"):
        build_red_mask(np.array([], dtype=np.uint8))
