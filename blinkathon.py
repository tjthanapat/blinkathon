import cv2
import numpy as np

from blink_detector import detect_faces, predict_landmarks, BlinkDetector
import blink_utilities as blink_utils
import camera_utilities as camera_utils


colors = [(0, 255, 0), (0, 100, 255)]

detecting_blink = False

N_FRAMES_TO_CALC_EAR_THRESH = 90


class Blinkathon:
    def __init__(self, cap: cv2.VideoCapture) -> None:
        self.cap = cap
        self.trackers = cv2.legacy.MultiTracker_create()
        self.rects = None
        self.blink_detectors = [
            BlinkDetector(),
            BlinkDetector(),
        ]
        self.status = None
        self.current_detected_faces = list()

    def generate_frames(self):
        global detecting_blink, n_frames_detect_blink

        while True:
            frame = camera_utils.read_video_capture(self.cap)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rects = detect_faces(gray)
            self.current_detected_faces = list()

            if (len(rects) == 0) or (len(self.trackers.getObjects()) < len(rects)):
                self.trackers = cv2.legacy.MultiTracker_create()
                for rect in rects:
                    bb = blink_utils.convert_rect_to_bb(rect)
                    tracker = blink_utils.OPENCV_OBJECT_TRACKERS["mosse"]()
                    self.trackers.add(tracker, frame, bb)

            (success, boxes) = self.trackers.update(frame)

            if success:
                for i, box in enumerate(boxes):
                    (x, y, w, h) = [int(v) for v in box]

                    if detecting_blink and i < 2:
                        landmarks = predict_landmarks(
                            frame,
                            blink_utils.convert_bb_to_rect((x, y, w, h)),
                        )
                        eye_landmarks = (
                            landmarks[42:48],  # left_eye
                            landmarks[36:42],  # right_eye
                        )
                        blink_utils.draw_eye_landmarks(
                            frame,
                            eye_landmarks,
                            color=colors[i % 2],
                        )
                        blink_detector = self.blink_detectors[i]
                        amount_of_frames = len(
                            blink_detector.first_n_eye_landmarks[0][0])
                        if amount_of_frames <= N_FRAMES_TO_CALC_EAR_THRESH:
                            if amount_of_frames == N_FRAMES_TO_CALC_EAR_THRESH:
                                blink_detector.store_first_n_eye_landmarks(
                                    eye_landmarks)
                                blink_detector.calculate_ear_thresh(
                                    blink_detector.first_n_eye_landmarks)
                            else:
                                blink_detector.store_first_n_eye_landmarks(
                                    eye_landmarks
                                )

                        else:
                            ear_score = blink_detector.detect_blink(
                                eye_landmarks)
                            cv2.putText(
                                frame,
                                f"EAR: {ear_score:.2f} | Count: {blink_detector.total_count}",
                                ((x + 5), (y + 30)),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.4,
                                colors[i % 2],
                                1,
                            )
                        cv2.putText(
                            frame,
                            f"THRESH: {blink_detector.ear_thresh:.2f}",
                            ((x + 5), (y + 15)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.4,
                            colors[i % 2],
                            1,
                        )

                    cv2.rectangle(frame, (x, y), (x + w, y + h),
                                  colors[i % 2], 2)
                    cv2.putText(
                        frame,
                        f"P{i+1}" if i < 2 else f"NPC {i-1}",
                        ((x + round(0.4 * w)), (y - 20)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        colors[i % 2],
                        2,
                    )
            self.status = dict(
                playable=len(boxes) >= 2,
                detecting=(len(self.blink_detectors[0].first_n_eye_landmarks[0][0]) >= N_FRAMES_TO_CALC_EAR_THRESH) and
                (len(self.blink_detectors[1].first_n_eye_landmarks[0]
                 [0]) >= N_FRAMES_TO_CALC_EAR_THRESH),
                players=[
                    dict(blinkCount=self.blink_detectors[0].total_count),
                    dict(blinkCount=self.blink_detectors[1].total_count),
                ],
            )

            frame = camera_utils.encode_frame(frame)
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

    def start_detect_blinks(self):
        global detecting_blink
        detecting_blink = True
        self.blink_detectors = [
            BlinkDetector(),
            BlinkDetector(),
        ]

    def stop_detect_blinks(self):
        global detecting_blink, n_frames_detect_blink
        detecting_blink = False
        self.blink_detectors = [
            BlinkDetector(),
            BlinkDetector(),
        ]
