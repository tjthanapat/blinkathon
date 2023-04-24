import cv2
import numpy as np
from typing import Tuple, List
import dlib
from imutils import face_utils
import face_recognition_models
import blink_utilities as blink_utils


frontal_face_detector = dlib.get_frontal_face_detector()
landmark_predictor = dlib.shape_predictor(
    face_recognition_models.pose_predictor_model_location()
)


def detect_faces(frame_gray: np.ndarray) -> List[dlib.rectangle]:
    rects = frontal_face_detector(frame_gray, 0)
    return list(rects)


def predict_landmarks(
    frame_gray: np.ndarray,
    rect: dlib.rectangle,
) -> np.ndarray:
    shape = landmark_predictor(frame_gray, rect)
    landmarks = face_utils.shape_to_np(shape)
    return landmarks


## TO DO ##

DEFAULT_EYE_AR_THRESH = 0.24
EYE_AR_CONSEC_FRAMES = 3


class BlinkDetector:
    def __init__(self) -> None:
        self.ear_thresh = DEFAULT_EYE_AR_THRESH
        self.total_count = 0
        self.consec_frame_count = 0
        self.first_n_eye_landmarks = list()

    def store_first_n_eye_landmarks(self, eye_landmarks):
        self.first_n_eye_landmarks.append(eye_landmarks)

    def calculate_ear_thresh(
        self,
        eye_landmarks: Tuple[np.ndarray, np.ndarray],
    ):
        ### Calculate adaptive threshold here
        ### Define required functions in blink_utils
        left_eye, right_eye = eye_landmarks
        left_eye_mEAR = blink_utils.cal_mEAR(left_eye)
        right_eye_mEAR = blink_utils.cal_mEAR(right_eye)
        new_ear_thresh = (left_eye_mEAR+right_eye_mEAR)/2
        self.ear_thresh = new_ear_thresh

    def detect_blink(
        self,
        eye_landmarks: Tuple[np.ndarray, np.ndarray],
    ):
        ### Calculate ear score here
        ### Define required functions in blink_utils
        left_eye, right_eye = eye_landmarks
        left_eye_EAR = blink_utils.cal_EAR(left_eye)
        right_eye_EAR = blink_utils.cal_EAR(right_eye)
        ear_score = (left_eye_EAR+right_eye_EAR)/2
        if ear_score <= self.ear_thresh:
            self.consec_frame_count += 1
        else:
            if self.consec_frame_count >= EYE_AR_CONSEC_FRAMES:
                self.total_count += 1
            self.consec_frame_count = 0
        
        return ear_score
