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

def find_min_max(mEAR_list, l_cal):
    mEAR_list[0] = min(l_cal[0], mEAR_list[0])
    mEAR_list[1] = min(l_cal[1], mEAR_list[1])
    mEAR_list[2] = max(l_cal[2], mEAR_list[2])

    mEAR_list[3] = max(l_cal[0], mEAR_list[3])
    mEAR_list[4] = max(l_cal[1], mEAR_list[4])
    mEAR_list[5] = min(l_cal[2], mEAR_list[5])
    
    return mEAR_list # first 3 positions are mEAR closed. last 3 positions are mEAR opened

def cal_mEAR(l_mEAR_list, r_mEAR_list):
    l_EAR_close = (l_mEAR_list[0]+l_mEAR_list[1])/(2.0*l_mEAR_list[2])
    l_EAR_open = (l_mEAR_list[3]+l_mEAR_list[4])/(2.0*l_mEAR_list[5])
    l_mEAR = (l_EAR_open + l_EAR_close)/2

    r_EAR_close = (r_mEAR_list[0]+r_mEAR_list[1])/(2.0*r_mEAR_list[2])
    r_EAR_open = (r_mEAR_list[3]+r_mEAR_list[4])/(2.0*r_mEAR_list[5])
    r_mEAR = (r_EAR_open + r_EAR_close)/2
    
    mEAR = (l_mEAR+r_mEAR)/2

    return mEAR-0.05

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

def random_color(amount):
    np.random.seed(123)
    color = []
    for _ in range(amount):
        r = np.random.randint(0,255)
        g = np.random.randint(0,255)
        b = np.random.randint(0,255)
        rgb = (r,g,b)
        color.append(rgb)
    return color

def detect_blink(frame, flag, count):
    global trackers
    frame= imutils.resize(frame, width=800)
    frame = cv2.flip(frame,1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)
    is_blink = [False]*len(rects) # assgin blink or not variable
    ear = [0]*len(rects) # assign EAR each person

    left_eye_cal = [] # index represent person
    right_eye_cal = []

   # if rects is more than tracker, then create new trackers and add tracker
    if (len(rects) == 0) or (len(trackers.getObjects()) < len(rects)):
        trackers = cv2.legacy.MultiTracker_create()
        flag = True

    # add tracker to each face
    for i in range(len(rects)):
        rect = rect_to_bb(rects[i])
        
        if flag:
            tracker = OPENCV_OBJECT_TRACKERS['mosse']()
            trackers.add(tracker, frame, rect)

    # get new bounding box (each face) from tracker
    (success, boxes) = trackers.update(frame)
    
    if success:
        # loop through each bounding box (each bounding box = each face = each person)
        for j in range(len(boxes)):
            x,y,w,h = int(boxes[j][0]),int(boxes[j][1]),int(boxes[j][2]),int(boxes[j][3])
            rect = bb_to_rect([int(v) for v in boxes[j]]) # convert to rect object for predict face landmark
            shape = predictor(gray, rect) # predict face landmark
            shape = face_utils.shape_to_np(shape)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color[j], 2)
            leftEye = shape[42:48]
            rightEye = shape[36:42]

            l_p2_p6 = euclidean(shape[43],shape[47])
            l_p3_p5 = euclidean(shape[44],shape[46])
            l_p1_p4 = euclidean(shape[42],shape[45])
            
            r_p2_p6 = euclidean(shape[37],shape[41])
            r_p3_p5 = euclidean(shape[38],shape[40])
            r_p1_p4 = euclidean(shape[36],shape[39])

            left_eye_cal.append([l_p2_p6, l_p3_p5, l_p1_p4])
            right_eye_cal.append([r_p2_p6, r_p3_p5, r_p1_p4])
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            ear[j] = (leftEAR + rightEAR) / 2.0 # update EAR person j
            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, color[j], 1)
            cv2.drawContours(frame, [rightEyeHull], -1, color[j], 1)
            cv2.putText(frame, "Blinks_{}: {} EAR_{}: {:.2f} mEAR_{}: {:.2f}".format(j, total[j], 
                                                                        j, ear[j], 
                                                                        j, minimun_ear[j]), (x-50, y-20),
                                                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color[j], 2) 

            if ear[j] <= minimun_ear[j]: # if ear person j less than threshold count frame +1
                count[j] += 1
                        
            else:
                if count[j] >= MINIMUM_FRAME: # if counted frame more than consecutive threshold then person j has blinked
                    is_blink[j] = True
                    
                count[j] = 0 # reset counted frame person j

    # assgin flag to false if tracker and person are equal      
    if flag and (len(trackers.getObjects()) >= len(rects)):            
        flag = False

    return frame, is_blink, count, flag, left_eye_cal, right_eye_cal

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

MINIMUM_FRAME = 3
minimun_ear = [0.18]*15

counter = [0]*15 # 15 is the most people we can handle
total = [0]*15
color= random_color(15)
trackers = cv2.legacy.MultiTracker_create()
flag = True

l_mEAR_list = [[999,999,0,0,0,999]]*15 # [p2-p6 (close), p3-p5(close), p1-p4(close), p2-p6 (open), p3-p5(open), p1-p4(open)]
r_mEAR_list = [[999,999,0,0,0,999]]*15

cap = cv2.VideoCapture("C:\\Users\\Gear\\Desktop\\Blinkathon\\test blinking2.mp4")
# cap = cv2.VideoCapture(0)

while cap.isOpened():
    
    ret, frame = cap.read()

    if not ret:
        break

    frame, blinked, counter, flag, l_cal, r_cal = detect_blink(frame, flag, counter)

    for i in range(len(blinked)):
        if blinked[i]:
            total[i] += 1

    for j in range(len(l_cal)):

        l_mEAR_list[j] = find_min_max(l_mEAR_list[j], l_cal[j])
        r_mEAR_list[j] = find_min_max(r_mEAR_list[j], r_cal[j])
        minimun_ear[j] = cal_mEAR(l_mEAR_list[j], r_mEAR_list[j])

    cv2.imshow("Frame", frame)
        
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        cap.release()
        cv2.destroyAllWindows()
        break

cap.release()
cv2.destroyAllWindows()