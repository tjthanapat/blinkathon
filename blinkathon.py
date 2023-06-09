import cv2
import numpy as np

from blink_detector import detect_faces, predict_landmarks, BlinkDetector
import blink_utilities as blink_utils


colors = [(0, 0, 255), (0, 255, 0)]

N_FRAMES_TO_CALC_EAR_THRESH = 90


class Blinkathon:
    def __init__(self) -> None:
        self.trackers = cv2.legacy.MultiTracker_create()
        self.rects = None
        self.blink_detectors = [
            BlinkDetector(),
            BlinkDetector(),
        ]
        self.playable = False
        self.detecting_blink = False

    def start_detect_blink(self):
        self.detecting_blink = True
        return self

    def stop_detect_blink(self):
        self.detecting_blink = False
        self.blink_detectors = [
            BlinkDetector(),
            BlinkDetector(),
        ]
        return self

    def get_status(self) -> dict:
        return dict(
            playable=self.playable,
            detecting_blink=self.detecting_blink, # กด start
            counting_blink=(
                len(self.blink_detectors[0].first_n_eye_landmarks[0][0]) \
                >= N_FRAMES_TO_CALC_EAR_THRESH) and \
                (len(self.blink_detectors[1].first_n_eye_landmarks[0][0]) \
                >= N_FRAMES_TO_CALC_EAR_THRESH
            ), # เริ่มกระพริบ
            players=[
                dict(blinkCount=self.blink_detectors[0].total_count),
                dict(blinkCount=self.blink_detectors[1].total_count),
            ],
        )

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detect_faces(gray)

        ### Implement face tracking here.
        if (len(rects) == 0) or (len(self.trackers.getObjects()) < len(rects)):
            self.trackers = cv2.legacy.MultiTracker_create()
            for rect in rects:
                bb = blink_utils.convert_rect_to_bb(rect)
                tracker = blink_utils.OPENCV_OBJECT_TRACKERS["mosse"]()
                self.trackers.add(tracker, frame, bb)

        self.playable = len(rects) >= 2
        
        (success, boxes) = self.trackers.update(frame)

        if success:
            for i, box in enumerate(boxes):
                (x, y, w, h) = [int(v) for v in box]
                color = colors[i] if i < 2 else (220, 220, 220)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(
                    frame,
                    f"P{i+1}" if i < 2 else f"NPC {i-1}",
                    ((x + round(0.4 * w)), (y - 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2,
                )

                if i < 2:
                    blink_detector = self.blink_detectors[i]
                    # cv2.putText(
                    #     frame,
                    #     f"THRESH: {blink_detector.ear_thresh}",
                    #     ((x + 5), (y + 15)),
                    #     cv2.FONT_HERSHEY_SIMPLEX,
                    #     0.4,
                    #     color,
                    #     1,
                    # )
                    if self.detecting_blink:
                        landmarks = predict_landmarks(
                            frame,
                            blink_utils.convert_bb_to_rect((x, y, w, h))
                        )
                        eye_landmarks = (
                            landmarks[42:48],  # left_eye
                            landmarks[36:42],  # right_eye
                        )
                        blink_utils.draw_eye_landmarks(
                            frame,
                            eye_landmarks,
                            color,
                        )
                        ### Modify EAR calculation here.
                        n_frames_detect_blink = len(blink_detector.first_n_eye_landmarks[0][0])
                        if n_frames_detect_blink <= N_FRAMES_TO_CALC_EAR_THRESH:
                            if n_frames_detect_blink == N_FRAMES_TO_CALC_EAR_THRESH:
                                blink_detector.store_first_n_eye_landmarks(eye_landmarks)
                                blink_detector.calculate_ear_thresh()
                            else:
                                blink_detector.store_first_n_eye_landmarks(eye_landmarks)
                        else:
                            ear_score = blink_detector.detect_blink(eye_landmarks)
                            # cv2.putText(
                            #     frame,
                            #     f"EAR: {ear_score:.2f} | Count: {blink_detector.total_count}",
                            #     ((x + 5), (y + 30)),
                            #     cv2.FONT_HERSHEY_SIMPLEX,
                            #     0.4,
                            #     color,
                            #     1,
                            # )

        return self, frame
