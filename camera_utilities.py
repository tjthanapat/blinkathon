from collections.abc import Iterator
import cv2
from custom_types import Frame


def read_video_capture(cap: cv2.VideoCapture) -> Frame:
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


def encode_frame(frame: Frame) -> bytes:
    """Encode frame to jpg bytes.

    Parameters
    ----------
    frame : array of image

    Returns
    -------
    bytes
    """
    success, frame = cv2.imencode(".jpg", frame)
    if not success:
        raise Exception("Cannot encode a frame.")
    return frame.tobytes()


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
        try:
            frame = read_video_capture(cap)
            frame = encode_frame(frame)
            yield (
                b"--frame\r\n" 
                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )
        except Exception as err:
            print(err)
            # emit('game', dict(errMessage=str(err)))
