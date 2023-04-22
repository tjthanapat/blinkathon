from collections.abc import Iterator
import cv2
import numpy as np


IMG = np.ndarray


def read_video_capture(cap: cv2.VideoCapture) -> IMG:
    """Read a frame from a given video capture.

    Parameters
    ----------
    cap : cv2.VideoCapture

    Returns
    -------
    array for image
    """
    ret, frame = cap.read()
    if not ret:
        raise Exception("Cannot read a frame from video capture.")
    return frame


def yeild_frame(frame: IMG) -> Iterator[bytes]:
    """Yeild frames encoded to bytes.

    Parameters
    ----------
    frame : array for image

    Yields
    ------
    Iterator[bytes]
    """
    success, frame = cv2.imencode(".jpg", frame)
    frame = frame.tobytes()
    if not success:
        raise Exception("Cannot encode a frame.")
    yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


def gen_frames(cap: cv2.VideoCapture) -> Iterator[bytes]:
    """Generate frames from a given video capture.

    Parameters
    ----------
    cap : cv2.VideoCapture

    Yields
    ------
    Iterator[bytes]
    """
    while True:
        frame = read_video_capture(cap)
        yeild_frame(frame)
