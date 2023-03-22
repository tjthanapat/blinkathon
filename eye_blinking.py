import cv2
from scipy.spatial import distance as dist
import imutils
from imutils import face_utils
import dlib


EYE_AR_THRESH = 0.2
EYE_AR_CONSEC_FRAMES = 3

# (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
# (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

(lStart, lEnd) = (36, 42)
(rStart, rEnd) = (42, 48)

def calculate_eye_aspect_ratio(eye):
    
    # compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    
    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = dist.euclidean(eye[0], eye[3])
    
    # compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)
    
    # return the eye aspect ratio
    return ear


def gen_blink_detect(video):
    COUNTER = 0
    TOTAL = 0
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    while True:
        success, frame = video.read()  # read the camera frame
        if not success:
            break
        else:
            frame = imutils.resize(frame, width=450)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # detect faces in the grayscale frame
            rects = detector(gray, 0)

            # loop over the face detections
            for rect in rects:
                
                # determine the facial landmarks for the face region, then
                # convert the facial landmark (x, y)-coordinates to a NumPy
                # array
                shape = predictor(gray, rect)
                shape = face_utils.shape_to_np(shape)
                
                # extract the left and right eye coordinates, then use the
                # coordinates to compute the eye aspect ratio for both eyes
                leftEye = shape[lStart:lEnd]
                rightEye = shape[rStart:rEnd]
                leftEAR = calculate_eye_aspect_ratio(leftEye)
                rightEAR = calculate_eye_aspect_ratio(rightEye)
                
                # average the eye aspect ratio together for both eyes
                ear = (leftEAR + rightEAR) / 2.0
                
                # compute the convex hull for the left and right eye, then
                # visualize each of the eyes
                leftEyeHull = cv2.convexHull(leftEye)
                rightEyeHull = cv2.convexHull(rightEye)
                cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
                cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
                
                # check to see if the eye aspect ratio is below the blink
                # threshold, and if so, increment the blink frame counter
                if ear < EYE_AR_THRESH:
                    COUNTER += 1
                    
                # otherwise, the eye aspect ratio is not below the blink
                # threshold
                else:
                    # if the eyes were closed for a sufficient number of
                    # then increment the total number of blinks
                    if COUNTER >= EYE_AR_CONSEC_FRAMES:
                        TOTAL += 1
                        
                    # reset the eye frame counter
                    COUNTER = 0
                    
                # draw the total number of blinks on the frame along with
                # the computed eye aspect ratio for the frame
                cv2.putText(frame, "Blinks: {}".format(TOTAL), (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            ret, jpeg = cv2.imencode('.jpg', frame)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                      b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    