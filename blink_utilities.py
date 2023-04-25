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


def euclidean(x: np.ndarray, y: np.ndarray):
    '''calculate euclidean distance'''

    euclidean_dist = np.sqrt(np.sum((x-y)**2))
    return euclidean_dist


def mEAR_closed(landmarks):
    ''' 
    calculate mEAR
    https://peerj.com/articles/cs-943/
    '''

    A = min(list(map(euclidean, landmarks[1], landmarks[5])))
    B = min(list(map(euclidean, landmarks[2], landmarks[4])))
    C = max(list(map(euclidean, landmarks[0], landmarks[3])))
    mEAR_close = (A + B) / (2.0 * C)

    return mEAR_close


def mEAR_open(landmarks):
    ''' calculate mEAR'''

    A = max(list(map(euclidean, landmarks[1], landmarks[5])))
    B = max(list(map(euclidean, landmarks[2], landmarks[4])))
    C = min(list(map(euclidean, landmarks[0], landmarks[3])))
    mEAR_open = (A + B) / (2.0 * C)

    return mEAR_open


def cal_mEAR(landmarks):
    return (mEAR_closed(landmarks)+mEAR_open(landmarks))/2


def cal_EAR(landmarks):
    ''' 
    calculate EAR
    https://pyimagesearch.com/2017/04/24/eye-blink-detection-opencv-python-dlib/?fbclid=IwAR0vstYc2Yqfjib_-GYPUcMPbmB2x74_4CqBStD1nxBhljoyIeQHoFr9VOE
    '''
    A = euclidean(landmarks[1], landmarks[5])
    B = euclidean(landmarks[2], landmarks[4])
    C = euclidean(landmarks[0], landmarks[3])

    ear = (A + B) / (2.0 * C)

    return ear
