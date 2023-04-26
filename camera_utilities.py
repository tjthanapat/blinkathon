import cv2
import numpy as np
import imutils


def read_video_capture(
    cap: cv2.VideoCapture,
    horizontal_flip: bool = True,
) -> np.ndarray:
    """Read a frame from a given video capture.

    Parameters
    ----------
    cap : cv2.VideoCapture
    horizontal_flip : bool, optional
        If true, frame is holizontally flipped, by default True

    Returns
    -------
    np.ndarray
        image array
    """
    ret, frame = cap.read()
    if not ret:
        raise Exception("Cannot read a frame from video capture.")
    if horizontal_flip:
        frame = cv2.flip(frame, 1)
    frame = imutils.resize(frame, width=800)
    return frame


def encode_frame(frame: np.ndarray) -> bytes:
    """Encode frame to jpg bytes.

    Parameters
    ----------
    frame : image array

    Returns
    -------
    bytes
    """
    success, frame = cv2.imencode(".jpg", frame)
    if not success:
        raise Exception("Cannot encode a frame.")
    return frame.tobytes()
