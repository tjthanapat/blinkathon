from typing import Tuple
import cv2
import numpy as np
import dlib


def convert_rect_to_bb(rect: dlib.rectangle) -> Tuple[int, int, int, int]:
    """Convert dlib rectangle to bounding box.

    Parameters
    ----------
    rect : dlib.rectangle
        dlib rectangle representing bounding box.

    Returns
    -------
    bb : tuple[x:int, y:int, w:int, h:int]
        Bounding box on a frame represented by its top-left point
        (x and y), width (w) and height (h).
    """
    x = rect.left()
    y = rect.top()
    w = rect.right() - x
    h = rect.bottom() - y

    return (x, y, w, h)


def convert_bb_to_rect(bb: Tuple[int, int, int, int]) -> dlib.rectangle:
    """Convert bounding box to dlib rectangle.

    Parameters
    ----------
    bb : tuple[x:int, y:int, w:int, h:int]
        Bounding box on a frame represented by its top-left point
        (x and y), width (w) and height (h).

    Returns
    -------
    dlib.rectangle
        dlib rectangle representing bounding box.
    """
    left = int(bb[0])
    top = int(bb[1])
    right = int(bb[2]) + left
    bottom = int(bb[3]) + top

    return dlib.rectangle(left, top, right, bottom)


OPENCV_OBJECT_TRACKERS = {
    "csrt": cv2.legacy.TrackerCSRT_create,
    "kcf": cv2.legacy.TrackerKCF_create,
    "boosting": cv2.legacy.TrackerBoosting_create,
    "mil": cv2.legacy.TrackerMIL_create,
    "tld": cv2.legacy.TrackerTLD_create,
    "medianflow": cv2.legacy.TrackerMedianFlow_create,
    "mosse": cv2.legacy.TrackerMOSSE_create,
}


def draw_eye_landmarks(
    frame,
    eye_landmarks: Tuple[np.ndarray, np.ndarray],
    color: Tuple[int, int, int],
):
    left_eye, right_eye = eye_landmarks
    left_eye_hull = cv2.convexHull(left_eye)
    right_eye_hull = cv2.convexHull(right_eye)
    cv2.drawContours(frame, [left_eye_hull], -1, color, 1)
    cv2.drawContours(frame, [right_eye_hull], -1, color, 1)
