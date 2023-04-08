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

def mEAR_closed(p1,p2,p3,p4,p5,p6):
    ''' 
    calculate mEAR
    https://peerj.com/articles/cs-943/
    '''
    try:
        A = min(np.array(list(map(euclidean, p2,p6))))
        B = min(np.array(list(map(euclidean, p3,p5))))
        C = max(np.array(list(map(euclidean, p1,p4))))
        mEAR_close = (A + B) / (2.0 * C)

    except:
        print('Cannot detect eye')
        cap.release()
        cv2.destroyAllWindows()
        exit()

    return   mEAR_close

def mEAR_open(p1,p2,p3,p4,p5,p6):
    ''' calculate mEAR'''
    try:
        A = max(np.array(list(map(euclidean, p2,p6))))
        B = max(np.array(list(map(euclidean, p3,p5))))
        C = min(np.array(list(map(euclidean, p1,p4))))
        mEAR_open = (A + B) / (2.0 * C)

    except:
        print('Cannot detect eye')
        cap.release()
        cv2.destroyAllWindows()
        exit()
    
    return mEAR_open

    

def blink_count(person_id, frame, rect, color):
    global threshold
    global measure
    global landmark

    if landmark[person_id]['P1_L'].shape[0] == 90:

        mEAR_L = ((mEAR_closed(landmark[person_id]['P1_L'],
                                    landmark[person_id]['P2_L'],
                                    landmark[person_id]['P3_L'],
                                    landmark[person_id]['P4_L'],
                                    landmark[person_id]['P5_L'],
                                    landmark[person_id]['P6_L'])+mEAR_open(landmark[person_id]['P1_L'],
                                                                            landmark[person_id]['P2_L'],
                                                                            landmark[person_id]['P3_L'],
                                                                            landmark[person_id]['P4_L'],
                                                                            landmark[person_id]['P5_L'],
                                                                            landmark[person_id]['P6_L']))/2)
        mEAR_R = ((mEAR_closed(landmark[person_id]['P1_R'],
                                    landmark[person_id]['P2_R'],
                                    landmark[person_id]['P3_R'],
                                    landmark[person_id]['P4_R'],
                                    landmark[person_id]['P5_R'],
                                    landmark[person_id]['P6_R'])+mEAR_open(landmark[person_id]['P1_R'],
                                                                            landmark[person_id]['P2_R'],
                                                                            landmark[person_id]['P3_R'],
                                                                            landmark[person_id]['P4_R'],
                                                                            landmark[person_id]['P5_R'],
                                                                            landmark[person_id]['P6_R']))/2)
        threshold[person_id]['EYE_AR_THRESH'] = ((mEAR_L+mEAR_R)/2)
     
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    shape = predictor(gray, rect)
    shape = face_utils.shape_to_np(shape)

    if landmark[person_id]['P1_L'].shape[0] <= 90:
        landmark[person_id]['P1_L'] = np.vstack((landmark[person_id]['P1_L'],[shape[42]]))
        landmark[person_id]['P2_L'] = np.vstack((landmark[person_id]['P2_L'],[shape[43]]))
        landmark[person_id]['P3_L'] = np.vstack((landmark[person_id]['P3_L'],[shape[44]]))
        landmark[person_id]['P4_L'] = np.vstack((landmark[person_id]['P4_L'],[shape[45]]))
        landmark[person_id]['P5_L'] = np.vstack((landmark[person_id]['P5_L'],[shape[46]]))
        landmark[person_id]['P6_L'] = np.vstack((landmark[person_id]['P6_L'],[shape[47]]))

        landmark[person_id]['P1_R'] = np.vstack((landmark[person_id]['P1_R'],[shape[36]]))
        landmark[person_id]['P2_R'] = np.vstack((landmark[person_id]['P2_R'],[shape[37]]))
        landmark[person_id]['P3_R'] = np.vstack((landmark[person_id]['P3_R'],[shape[38]]))
        landmark[person_id]['P4_R'] = np.vstack((landmark[person_id]['P4_R'],[shape[39]]))
        landmark[person_id]['P5_R'] = np.vstack((landmark[person_id]['P5_R'],[shape[40]]))
        landmark[person_id]['P6_R'] = np.vstack((landmark[person_id]['P6_R'],[shape[41]]))



    leftEye = shape[42:48]
    rightEye = shape[36:42]
    leftEAR = eye_aspect_ratio(leftEye)
    rightEAR = eye_aspect_ratio(rightEye)
    ear = (leftEAR + rightEAR) / 2.0

    leftEyeHull = cv2.convexHull(leftEye)
    rightEyeHull = cv2.convexHull(rightEye)
    cv2.drawContours(frame, [leftEyeHull], -1, color, 1)
    cv2.drawContours(frame, [rightEyeHull], -1, color, 1)

    if ear <= threshold[person_id]['EYE_AR_THRESH']:
        measure[person_id]['COUNTER'] += 1
                
    else:
        if measure[person_id]['COUNTER'] >= threshold[person_id]['EYE_AR_CONSEC_FRAMES']:
            measure[person_id]['TOTAL'] += 1
            
        measure[person_id]['COUNTER'] = 0
 
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

def text_on_frame(person_id, x, y):
    y = int(y)
    x = int(x)
    cv2.putText(frame, "Blinks_{}: {} EAR_{}: {:.2f} mEAR_{}: {:.2f}".format(person_id, measure[person_id]['TOTAL'], 
                                                                            person_id, ear[person_id]['ear'], 
                                                                            person_id, threshold[person_id]['EYE_AR_THRESH']), (x, y),
                                                                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color[person_id], 2)

minimum_frame = 2
minimun_ear = 0.24

threshold = {0:{'EYE_AR_THRESH':minimun_ear,
                'EYE_AR_CONSEC_FRAMES':minimum_frame},
                1:{'EYE_AR_THRESH':minimun_ear,
                'EYE_AR_CONSEC_FRAMES':minimum_frame}}


measure = {0:{'COUNTER':0,
              'TOTAL':0},
              1:{'COUNTER':0,
              'TOTAL':0}}

landmark = {0:{'P1_L':np.empty((0,2)),
               'P2_L':np.empty((0,2)),
                'P3_L':np.empty((0,2)),
                'P4_L':np.empty((0,2)),
                'P5_L':np.empty((0,2)),
                'P6_L':np.empty((0,2)),
                'P1_R':np.empty((0,2)),
                'P2_R':np.empty((0,2)),
                'P3_R':np.empty((0,2)),
                'P4_R':np.empty((0,2)),
                'P5_R':np.empty((0,2)),
                'P6_R':np.empty((0,2))},
                1:{'P1_L':np.empty((0,2)),
               'P2_L':np.empty((0,2)),
                'P3_L':np.empty((0,2)),
                'P4_L':np.empty((0,2)),
                'P5_L':np.empty((0,2)),
                'P6_L':np.empty((0,2)),
                'P1_R':np.empty((0,2)),
                'P2_R':np.empty((0,2)),
                'P3_R':np.empty((0,2)),
                'P4_R':np.empty((0,2)),
                'P5_R':np.empty((0,2)),
                'P6_R':np.empty((0,2))}}


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

cap = cv2.VideoCapture(0)

trackers = cv2.legacy.MultiTracker_create()
flag = True
color= [(0,255,0),(0,100,255)]
ear = {0:{'ear':0.00},
        1:{'ear':0.00}}
boxes = []
success = False

while cap.isOpened():

    ret, frame = cap.read()

    if ret:
        frame= imutils.resize(frame, width=800)
        frame = cv2.flip(frame,1)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)

        # print('find {} people'.format(len(rects)))
        if (len(rects) == 0) or (len(trackers.getObjects()) < len(rects)):
            trackers = cv2.legacy.MultiTracker_create()
            flag = True

        # print('flag: ',flag)
        for i in range(len(rects)):
            rect = rect_to_bb(rects[i])
            
            if flag:
                tracker = OPENCV_OBJECT_TRACKERS['mosse']()
                trackers.add(tracker, frame, rect)
                # print('tracker added')
                
            # print('now I have {} trackers and {} rects'.format(len(trackers.getObjects()),len(rects)))

        (success, boxes) = trackers.update(frame)

        # print('update tracker', success)
        if success:        
            for j in range(len(boxes)):
                try:
                    (x,y,w,h) = [int(v) for v in boxes[j]]
                    ear[j]['ear'] = blink_count(j,frame,bb_to_rect([x,y,w,h]),color[j])
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color[j], 2)
                    text_on_frame(j,(x-50),(y-20))
                except Exception as e:
                    print(e)

        cv2.imshow("Frame", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            cap.release()
            cv2.destroyAllWindows()
            break

        if flag and (len(trackers.getObjects()) >= len(rects)):            
            flag = False
        # print('End frame flag: ',flag)

    else:
        cap.release()
        cv2.destroyAllWindows()
        # print("END")
    
cap.release()
cv2.destroyAllWindows()
