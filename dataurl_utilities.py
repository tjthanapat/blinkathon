import urllib
import cv2
import numpy as np
import base64

def decode_dataurl_to_frame(frame_dataurl:str):
    res = urllib.request.urlopen(frame_dataurl)
    frame = np.asarray(bytearray(res.read()), dtype="uint8")
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    frame = cv2.flip(frame, 1)
    return frame


def encode_frame(frame:np.ndarray):
    retval, buffer = cv2.imencode('.jpg', frame)
    string = base64.b64encode(buffer).decode('utf-8')
    frame_dataurl = f'data:image/jpg;base64,{string}'

    return frame_dataurl