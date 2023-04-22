from imutils import face_utils
import imutils
import numpy as np
import dlib
import cv2
import face_recognition_models


def euclidean(x,y):
    ''' calculate euclidean distance'''
    euclidean_dist = np.sqrt(np.sum((x-y)**2))
    return euclidean_dist

def eye_aspect_ratio(eye):
    ''' 
    calculate EAR
    https://pyimagesearch.com/2017/04/24/eye-blink-detection-opencv-python-dlib/?fbclid=IwAR0vstYc2Yqfjib_-GYPUcMPbmB2x74_4CqBStD1nxBhljoyIeQHoFr9VOE
    '''
    A = euclidean(eye[1], eye[5])
    B = euclidean(eye[2], eye[4])
    C = euclidean(eye[0], eye[3])

    ear = (A + B) / (2.0 * C)
    
    return ear

def rect_to_bb(rect):
    ''' from dlib to opencv '''
    x = rect.left()
    y = rect.top()
    w = rect.right() - x
    h = rect.bottom() - y

    return (x, y, w, h)

def bb_to_rect(bb):
    ''' from opencv to dlib 
    input = [x,y,w,h]'''

    left = int(bb[0])
    top = int(bb[1])
    right = int(bb[2]) + left
    bottom = int(bb[3]) + top

    return dlib.rectangle(left, top, right, bottom)

def detect_blink(frame, flag):
    global trackers
    frame= imutils.resize(frame, width=800)
    frame = cv2.flip(frame,1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)
   
    if (len(rects) == 0) or (len(trackers.getObjects()) < len(rects)):
        trackers = cv2.legacy.MultiTracker_create()
        flag = True

    for i in range(len(rects)):
        rect = rect_to_bb(rects[i])
        
        if flag:
            tracker = OPENCV_OBJECT_TRACKERS['mosse']()
            trackers.add(tracker, frame, rect)

    (success, boxes) = trackers.update(frame)
    
    if success:
        # print(len(boxes))
        for j in range(len(boxes)):
            x,y,w,h = int(boxes[j][0]),int(boxes[j][1]),int(boxes[j][2]),int(boxes[j][3])
            rect = bb_to_rect([int(v) for v in boxes[j]])
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color[j], 2)
            leftEye = shape[42:48]
            rightEye = shape[36:42]
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            ear[j] = (leftEAR + rightEAR) / 2.0
            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, color[j], 1)
            cv2.drawContours(frame, [rightEyeHull], -1, color[j], 1)
            cv2.putText(frame, "Blinks_{}: {} EAR_{}: {:.2f} mEAR_{}: {:.2f}".format(j, total[j], 
                                                                        j, ear[j], 
                                                                        j, minimun_ear), (x-50, y-20),
                                                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color[j], 2)

            if ear[j] <= minimun_ear:
                counter[j] += 1
                        
            else:
                if counter[j] >= minimum_frame:
                    is_blink[j] = True
                    
                counter[j] = 0
    if flag and (len(trackers.getObjects()) >= len(rects)):            
        flag = False

    return frame, is_blink[0], is_blink[1], counter[0], counter[1], flag

OPENCV_OBJECT_TRACKERS = {
	"csrt": cv2.legacy.TrackerCSRT_create,
	"kcf": cv2.legacy.TrackerKCF_create,
	"boosting": cv2.legacy.TrackerBoosting_create,
	"mil": cv2.legacy.TrackerMIL_create,
	"tld": cv2.legacy.TrackerTLD_create,
	"medianflow": cv2.legacy.TrackerMedianFlow_create,
	"mosse": cv2.legacy.TrackerMOSSE_create
}

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(face_recognition_models.pose_predictor_model_location())

color= [(0,255,0),(0,100,255)]
minimum_frame = 3
minimun_ear = 0.24

counter = [0,0]
total = [0,0]
is_blink = [False,False]

cap = cv2.VideoCapture("C:\\Users\\Gear\\Desktop\\Blinkathon\\test blinking2.mp4")
# cap = cv2.VideoCapture(0)

trackers = cv2.legacy.MultiTracker_create()
flag = True

ear = [0,0]

while cap.isOpened():
    
    ret, frame = cap.read()

    if not ret:
        break

    frame, is_blink[0], is_blink[1], counter[0], counter[1], flag2 = detect_blink(frame, flag)
    
    flag = flag2
    if is_blink[0]:
        total[0] += 1
    if is_blink[1]:
        total[1] += 1
    is_blink[0]=0
    is_blink[1]=0
    cv2.imshow("Frame", frame)
        
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        cap.release()
        cv2.destroyAllWindows()
        break


cap.release()
cv2.destroyAllWindows()