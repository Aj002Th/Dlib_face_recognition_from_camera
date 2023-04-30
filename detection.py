from imutils import face_utils
import random
import numpy as np
 
 
def _help():
    print("Usage:")
    print("     python blink_detect.py")
    print("     python blink_detect.py <path of a video>")
    print("For example:")
    print("     python blink_detect.py video/lee.mp4")
    print("If the path of a video is not provided, the camera will be used as the input.Press q to quit.")
 
 
def eye_aspect_ratio(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    ear = (A + B) / (2.0 * C)
 
    return ear


def mouth_aspect_ratio(mouth):
    A = np.linalg.norm(mouth[2] - mouth[9])  # 51, 59
    B = np.linalg.norm(mouth[4] - mouth[7])  # 53, 57
    C = np.linalg.norm(mouth[0] - mouth[6])  # 49, 55
    mar = (A + B) / (2.0 * C)
 
    return mar
 
 

 
class Detector(object):
    """ 
    This class is used to detect the blink and mouth open.
    """
    EAR_THRESH = 0.2
    EAR_CONSEC_FRAMES_MIN = 1
    EAR_CONSEC_FRAMES_MAX = 2
    MAR_THRESH = 0.5
    def __init__(self) -> None:
        # initialize the frame counters and the total number of blinks
        self.blink_counter = [0, 0]  # left eye and right eye
        self.blink_total = [0, 0]  # left eye and right eye
    
        # grab the indexes of the facial landmarks for the left and
        # right eye, respectively
        (self.lStart, self.lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (self.rStart, self.rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

        # grab the indexes of the facial landmarks for the mouth
        (self.mStart, self.mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]
        # initialize the frame counter for mouth
        self.open_mouth = False

        # initialize the modes
        self.modes = ["blink", "mouth"]
        random.shuffle(self.modes)
        self.modes = [None] + self.modes + ['OK']
        self.current_mode = 0
        self.current_framecnt = None

    def compute(self, shape, frame_cnt=0):
        self.current_framecnt = frame_cnt
        shape = face_utils.shape_to_np(shape)
        left_eye = shape[self.lStart:self.lEnd]
        right_eye = shape[self.rStart:self.rEnd]
        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)

        # check to see if the eye aspect ratio is below the blink
        # threshold, and if so, increment the blink frame counter
        if left_ear < self.EAR_THRESH:
            self.blink_counter[0] += 1

        # otherwise, the eye aspect ratio is not below the blink
        # threshold
        else:
            # if the eyes were closed for a sufficient number of
            # then increment the total number of blinks
            if self.EAR_CONSEC_FRAMES_MIN <= self.blink_counter[0] and self.blink_counter[0] <= self.EAR_CONSEC_FRAMES_MAX:
                self.blink_total[0] += 1

            self.blink_counter[0] = 0

        # check to see if the eye aspect ratio is below the blink
        # threshold, and if so, increment the blink frame counter
        if right_ear < self.EAR_THRESH:
            self.blink_counter[1] += 1

        # otherwise, the eye aspect ratio is not below the blink
        # threshold
        else:
            # if the eyes were closed for a sufficient number of
            # then increment the total number of blinks
            if self.EAR_CONSEC_FRAMES_MIN <= self.blink_counter[1] and self.blink_counter[1] <= self.EAR_CONSEC_FRAMES_MAX:
                self.blink_total[1] += 1

            self.blink_counter[1] = 0

        # detect mouth open
        mouth = shape[self.mStart:self.mEnd]
        mar = mouth_aspect_ratio(mouth)

        if mar > self.MAR_THRESH:
            self.open_mouth = True
    
    def reset(self, mode=0):
        self.blink_counter = [0, 0]
        self.blink_total = [0, 0]
        self.open_mouth = False
        self.current_mode = mode
        self.last_framecnt = None
    
    def mode(self):
        return self.modes[self.current_mode]
        
    def blink(self):
        return self.blink_total[0] >= 1 and self.blink_total[1] >= 1

    def mouth(self):
        return self.open_mouth
    
    def next_mode(self):
        self.reset(self.current_mode+1)
        return self.mode()

    def check(self, frame_cnt=0):
        # check if the face is detected
        if self.current_framecnt != frame_cnt:
            self.reset()

        # check liveness
        flg = True
        if self.mode() == "blink":
            flg = self.blink()
        elif self.mode() == "mouth":
            flg = self.mouth()

        # print(self.mode(), flg)
        # check if the mode should be changed
        if flg:
            self.next_mode()

        return self.mode() == "OK"