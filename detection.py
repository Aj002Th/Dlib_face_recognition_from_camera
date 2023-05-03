from typing import Any
from imutils import face_utils
import cv2
import math
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

class GetHeadPose(object):
    """ 
    通过dlib获取人脸姿态
    """
    # 世界坐标系(UVW)：填写3D参考点，该模型参考http://aifi.isr.uc.pt/Downloads/OpenGL/glAnthropometric3DModel.cpp
    object_pts = np.float32([[6.825897, 6.760612, 4.402142],  #33左眉左上角
                            [1.330353, 7.122144, 6.903745],  #29左眉右角
                            [-1.330353, 7.122144, 6.903745], #34右眉左角
                            [-6.825897, 6.760612, 4.402142], #38右眉右上角
                            [5.311432, 5.485328, 3.987654],  #13左眼左上角
                            [1.789930, 5.393625, 4.413414],  #17左眼右上角
                            [-1.789930, 5.393625, 4.413414], #25右眼左上角
                            [-5.311432, 5.485328, 3.987654], #21右眼右上角
                            [2.005628, 1.409845, 6.165652],  #55鼻子左上角
                            [-2.005628, 1.409845, 6.165652], #49鼻子右上角
                            [2.774015, -2.080775, 5.048531], #43嘴左上角
                            [-2.774015, -2.080775, 5.048531],#39嘴右上角
                            [0.000000, -3.116408, 6.097667], #45嘴中央下角
                            [0.000000, -7.415691, 4.070434]])#6下巴角

    # 相机坐标系(XYZ)：添加相机内参
    K = [6.5308391993466671e+002, 0.0, 3.1950000000000000e+002,
        0.0, 6.5308391993466671e+002, 2.3950000000000000e+002,
        0.0, 0.0, 1.0]# 等价于矩阵[fx, 0, cx; 0, fy, cy; 0, 0, 1]
    # 图像中心坐标系(uv)：相机畸变参数[k1, k2, p1, p2, k3]
    D = [7.0834633684407095e-002, 6.9140193737175351e-002, 0.0, 0.0, -1.3073460323689292e+000]

    # 像素坐标系(xy)：填写凸轮的本征和畸变系数
    cam_matrix = np.array(K).reshape(3, 3).astype(np.float32)
    dist_coeffs = np.array(D).reshape(5, 1).astype(np.float32)



    # 重新投影3D点的世界坐标轴以验证结果姿势
    reprojectsrc = np.float32([[10.0, 10.0, 10.0],
                            [10.0, 10.0, -10.0],
                            [10.0, -10.0, -10.0],
                            [10.0, -10.0, 10.0],
                            [-10.0, 10.0, 10.0],
                            [-10.0, 10.0, -10.0],
                            [-10.0, -10.0, -10.0],
                            [-10.0, -10.0, 10.0]])
    # 绘制正方体12轴
    line_pairs = [[0, 1], [1, 2], [2, 3], [3, 0],
                [4, 5], [5, 6], [6, 7], [7, 4],
                [0, 4], [1, 5], [2, 6], [3, 7]]
    def __init__(self) -> None:
        pass
    def __repr__(self) -> str:
        return f'GetHeadPose()'
    def __call__(self, shape) -> Any:
        # （像素坐标集合）填写2D参考点，注释遵循https://ibug.doc.ic.ac.uk/resources/300-W/
        # 17左眉左上角/21左眉右角/22右眉左上角/26右眉右上角/36左眼左上角/39左眼右上角/42右眼左上角/
        # 45右眼右上角/31鼻子左上角/35鼻子右上角/48左上角/54嘴右上角/57嘴中央下角/8下巴角
        image_pts = np.float32([shape[17], shape[21], shape[22], shape[26], shape[36],
                                shape[39], shape[42], shape[45], shape[31], shape[35],
                                shape[48], shape[54], shape[57], shape[8]])
        # solvePnP计算姿势——求解旋转和平移矩阵：
        # rotation_vec表示旋转矩阵，translation_vec表示平移矩阵，cam_matrix与K矩阵对应，dist_coeffs与D矩阵对应。
        _, rotation_vec, translation_vec = cv2.solvePnP(self.object_pts, image_pts, self.cam_matrix, self.dist_coeffs)
        # projectPoints重新投影误差：原2d点和重投影2d点的距离（输入3d点、相机内参、相机畸变、r、t，输出重投影2d点）
        reprojectdst, _ = cv2.projectPoints(self.reprojectsrc, rotation_vec, translation_vec, self.cam_matrix, self.dist_coeffs)
        reprojectdst = tuple(map(tuple, reprojectdst.reshape(8, 2)))# 以8行2列显示

        # 计算欧拉角calc euler angle
        # 参考https://docs.opencv.org/2.4/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html#decomposeprojectionmatrix
        rotation_mat, _ = cv2.Rodrigues(rotation_vec)#罗德里格斯公式（将旋转矩阵转换为旋转向量）
        pose_mat = cv2.hconcat((rotation_mat, translation_vec))# 水平拼接，vconcat垂直拼接
        # decomposeProjectionMatrix将投影矩阵分解为旋转矩阵和相机矩阵
        _, _, _, _, _, _, euler_angle = cv2.decomposeProjectionMatrix(pose_mat)
        
        pitch, yaw, roll = [math.radians(_) for _ in euler_angle]
    
    
        pitch = math.degrees(math.asin(math.sin(pitch)))
        roll = -math.degrees(math.asin(math.sin(roll)))
        yaw = math.degrees(math.asin(math.sin(yaw)))
        # print('pitch:{}, yaw:{}, roll:{}'.format(pitch, yaw, roll))

        return reprojectdst, euler_angle# 投影误差，欧拉角

 

 
class Detector(object):
    """ 
    This class is used to detect the blink and mouth open and head pose.
    """
    EAR_THRESH = 0.2
    EAR_CONSEC_FRAMES_MIN = 1
    EAR_CONSEC_FRAMES_MAX = 4
    MAR_THRESH = 0.6
    HAR_THRESH = 2
    HAR_STAT = 0
    CLOCK_LIMIT = 100 # 如果一直没变就跳回去

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
        self.modes = ["blink", "mouth", "nod"]
        random.shuffle(self.modes)
        self.modes = [None] + self.modes + ['OK']
        self.current_mode = 0
        self.current_framecnt = None
        self.get_head_pose = GetHeadPose()

        # 计时器
        self.clock = 0

    def compute(self, shape, frame_cnt=0):
        self.current_framecnt = frame_cnt
        shape = face_utils.shape_to_np(shape)

        ############################################################
        ########################## eye ###########################
        ############################################################
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

        ############################################################
        ########################## mouth ###########################
        ############################################################
        # detect mouth open
        mouth = shape[self.mStart:self.mEnd]
        mar = mouth_aspect_ratio(mouth)
        if mar > self.MAR_THRESH:
            self.open_mouth = True

        ############################################################
        ########################## head ############################
        ############################################################
        reprojectdst, euler_angle = self.get_head_pose(shape)
        har = euler_angle[0, 0]
        if har > self.HAR_THRESH and self.HAR_STAT % 2 == 0:
            self.HAR_STAT += 1
        elif har < -self.HAR_THRESH and self.HAR_STAT % 2 == 1:
            self.HAR_STAT += 1

    
    def reset(self, mode=0):
        self.blink_counter = [0, 0]
        self.blink_total = [0, 0]
        self.open_mouth = False
        self.current_mode = mode
        self.last_framecnt = None
        self.HAR_STAT = 0
        if self.current_mode == 0:
            self.modes = ["blink", "mouth", "nod"]
            random.shuffle(self.modes)
            self.modes = [None] + self.modes + ['OK']
    
    def mode(self):
        return self.modes[self.current_mode]
        
    def blink(self):
        return self.blink_total[0] >= 1 and self.blink_total[1] >= 1

    def mouth(self):
        return self.open_mouth
    
    def nod(self):
        return self.HAR_STAT >= 4
    
    def next_mode(self):
        self.reset(self.current_mode+1)
        return self.mode()

    def check(self, frame_cnt=0):
        print(f'modes: {self.modes}')
        # check if the face is detected, or reset the detector
        if self.current_framecnt != frame_cnt or self.clock >= self.CLOCK_LIMIT:
            self.reset()

        # check liveness
        flg = True
        if self.mode() != None and self.mode() != "OK":
            flg = eval(f'self.{self.mode()}()')

        # print(self.mode(), flg)
        # check if the mode should be changed
        if flg:
            self.next_mode()
            self.clock = 0

        return self.mode() == "OK"