import dlib
import numpy as np
import cv2
import os
import pandas as pd
import time
from PIL import Image, ImageDraw, ImageFont
import random
import logging
from detection import Detector
from multiprocessing import Process, Queue
from threading import Thread

# logging.basicConfig(filename="test.log", filemode="w", format="%(asctime)s %(name)s:%(levelname)s:%(message)s", datefmt="%d-%M-%Y %H:%M:%S", level=logging.DEBUG)

# Dlib 正向人脸检测器 / Use frontal face detector of Dlib
detector = dlib.get_frontal_face_detector()

# Dlib 人脸 landmark 特征点检测器 / Get face landmarks
predictor = dlib.shape_predictor('data/data_dlib/shape_predictor_68_face_landmarks.dat')

# Dlib Resnet 人脸识别模型, 提取 128D 的特征矢量 / Use Dlib resnet50 model to get 128D face descriptor
face_reco_model = dlib.face_recognition_model_v1("data/data_dlib/dlib_face_recognition_resnet_model_v1.dat")

# 用多线程加速处理 / Enable multi-threading to accelerate face detection speed
# class Thread_get_feature(Thread):
#     def __init__(self, feature=None, img=None, shape=None):
#         super().__init__()
#         self.feature = feature
#         self.img = img
#         self.shape = shape
#         self.result = None

#     @staticmethod
#     def return_euclidean_distance(feature_1, feature_2):
#         feature_1 = np.array(feature_1)
#         feature_2 = np.array(feature_2)
#         dist = np.sqrt(np.sum(np.square(feature_1 - feature_2)))
#         return dist
    
#     def reset(self, feature, img, shape):
#         self.feature = feature
#         self.img = img
#         self.shape = shape
#         self.result = None

#     def run(self):
#         # Compute face descriptor using neural network defined in Dlib.
#         logging.debug('process start')
#         feature = face_reco_model.compute_face_descriptor(self.img, self.shape)
#         logging.debug('get feature')
#         if self.return_euclidean_distance(feature, self.feature) < 0.4:
#             self.result = True
#         else:
#             self.result = False
#         logging.debug('process end')

class Face_Recognizer:
    def __init__(self, name):
        self.name = name

        # Update FPS
        self.fps = 0                    # FPS of current frame
        self.fps_show = 0               # FPS per second
        self.frame_start_time = 0
        self.frame_cnt = 0
        self.start_time = time.time()

        self.font = cv2.FONT_ITALIC
        self.font_chinese = ImageFont.truetype("simsun.ttc", 30)
        self.current_centroid = None

        # 日志初始化 / Logging initialization
        self.log_path = os.path.join(os.curdir, 'logs')
        self.logger = logging.getLogger('audit')

    # 从 "features_all.csv" 读取录入人脸特征 / Read known faces from "features_all.csv"
    def get_face_database(self):
        if os.path.exists("data/features_all.csv"):
            path_features_known_csv = "data/features_all.csv"
            csv_rd = pd.read_csv(path_features_known_csv, header=None)
            self.face_feature = []
            for i in range(csv_rd.shape[0]):
                if csv_rd.iloc[i][0] == self.name:
                    for j in range(1, 129):
                        if csv_rd.iloc[i][j] == '':
                            self.face_feature.append('0')
                        else:
                            self.face_feature.append(csv_rd.iloc[i][j])
                    break
            if self.face_feature == []:
                logging.warning("no face in data/features_all.csv")
                return 0
            return 1
        else:
            logging.warning("'features_all.csv' not found!")
            logging.warning("Please run 'get_faces_from_camera.py' "
                            "and 'features_extraction_to_csv.py' before 'face_reco_from_camera.py'")
            return 0

    # 计算两个128D向量间的欧式距离 / Compute the e-distance between two 128D features
    @staticmethod
    def return_euclidean_distance(feature_1, feature_2):
        feature_1 = np.array(feature_1)
        feature_2 = np.array(feature_2)
        dist = np.sqrt(np.sum(np.square(feature_1 - feature_2)))
        return dist
    
    # 求质心 / Compute centroid
    @staticmethod
    def compute_centroid(face_position):
        centroid = (int((face_position.left() + face_position.right()) / 2),
                    int((face_position.top() + face_position.bottom()) / 2))
        return centroid

    # 更新 FPS / Update FPS of Video stream
    def update_fps(self):
        now = time.time()
        # 每秒刷新 fps / Refresh fps per second
        if str(self.start_time).split(".")[0] != str(now).split(".")[0]:
            self.fps_show = self.fps
        self.start_time = now
        self.frame_time = now - self.frame_start_time
        self.fps = 1.0 / self.frame_time
        self.frame_start_time = now

    # 生成的 cv2 window 上面添加说明文字 / PutText on cv2 window
    def draw_note(self, img_rd, note='please look at the camera'):
        cv2.putText(img_rd, "Face Recognizer", (20, 40), self.font, 1, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(img_rd, "Frame:  " + str(self.frame_cnt), (20, 100), self.font, 0.8, (0, 255, 0), 1,
                    cv2.LINE_AA)
        cv2.putText(img_rd, "FPS:    " + str(self.fps_show.__round__(2)), (20, 130), self.font, 0.8, (0, 255, 0), 1,
                    cv2.LINE_AA)
        cv2.putText(img_rd, "Q: Quit", (20, 160), self.font, 0.8, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(img_rd, note, (20, 200), self.font, 0.8, (0, 0, 255), 1, cv2.LINE_AA)

    def draw_name(self, img_rd):
        # 在人脸框下面写人脸名字 / Write names under rectangle
        img = Image.fromarray(cv2.cvtColor(img_rd, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img)
        for i in range(self.current_frame_face_cnt):
            # cv2.putText(img_rd, self.current_frame_face_name_list[i], self.current_frame_face_name_position_list[i], self.font, 0.8, (0, 255, 255), 1, cv2.LINE_AA)
            draw.text(xy=self.current_frame_face_name_position_list[i], text=self.current_frame_face_name_list[i], font=self.font_chinese,
                  fill=(255, 255, 0))
            img_rd = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        return img_rd

    # 修改显示人名 / Show names in chinese
    def show_chinese_name(self):
        # Default known name: person_1, person_2, person_3
        if self.current_frame_face_cnt >= 1:
            # 修改录入的人脸姓名 / Modify names in face_name_known_list to chinese name
            self.face_name_known_list[0] = '张三'
            # self.face_name_known_list[1] = '张四'.encode('utf-8').decode()
    
    # 模式的提示文字 / Info of mode
    def mode_to_notes(self, mode=None):
        if mode == None:
            return 'please look at the camera'
        elif mode == 'blink':
            return 'please blink your eyes'
        elif mode == 'mouth':
            return 'please open your mouth'
        elif mode == 'nod':
            return 'please nod your head'
    
    # 日志记录 / Logging
    def write_log_to_file(self, img, stat=None):
        time_str = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        # 保存图片到 log 目录 / Save images to log file
        img_path = os.path.join(self.log_path, 'img_face')
        if not os.path.exists(img_path):
            os.makedirs(img_path)
        img_path = os.path.join(img_path, time_str + '.jpg')
        cv2.imwrite(img_path, img)

        # 保存识别信息到 log.txt / Save information to log.txt
        log_info = ''
        log_info += 'Time: ' + str(time_str) + '\n\t'
        log_info += 'Name: ' + str(self.name) + '\n\t'
        log_info += 'Image path: ' + str(img_path) + '\n\t'
        log_info += 'Stat: ' + str(stat) + '\n'
        self.logger.info(log_info)
        

    # 处理获取的视频流，进行人脸识别 / Face detection and recognition from input video stream
    def process(self, stream):
        # 1. 读取存放所有人脸特征的 csv / Read known faces from "features.all.csv"
        liveness = Detector() # 活体检测器 / Liveness Detector
        # initialize centroid
        self.current_centroid = (stream.get(cv2.CAP_PROP_FRAME_WIDTH) / 2, stream.get(cv2.CAP_PROP_FRAME_HEIGHT) / 2)
        # 是不是那张脸 / Is it that face?
        face_is = False
        # 人脸计时器 / Face timer
        face_timer = 0
        # 开始时间 / Start time
        start_time = time.time()
        if self.get_face_database():
            while stream.isOpened():
                face_timer += 1
                self.frame_cnt += 1
                logging.debug("Frame %d starts", self.frame_cnt)
                flag, img_rd = stream.read()
                faces = detector(img_rd, 0)
                kk = cv2.waitKey(1)

                note = self.mode_to_notes(liveness.mode())
                self.draw_note(img_rd, note)
                
                # 2. 检测到人脸 / when face detected
                if len(faces) != 0:
                    current_centroid_list = []
                    for face in faces:
                        current_centroid_list.append(self.compute_centroid(face))
                    e_distance_list = []
                    for centroid in current_centroid_list:
                        e_distance_list.append(self.return_euclidean_distance(centroid, self.current_centroid))
                    target_face = faces[e_distance_list.index(min(e_distance_list))]

                    # predict face
                    shape = predictor(img_rd, target_face)
                    
                    # randomly check face
                    randomrate = 10
                    if self.frame_cnt % randomrate == random.randint(0, randomrate):
                        face_is = False
                        feature = face_reco_model.compute_face_descriptor(img_rd, shape)
                        e_distance = self.return_euclidean_distance(feature, self.face_feature)
                        if e_distance < 0.4:
                            face_is = True
                            face_timer = 0
                            liveness.compute(shape=shape, frame_cnt=self.frame_cnt)
                    elif face_is == True:
                        face_timer = 0
                        liveness.compute(shape=shape, frame_cnt=self.frame_cnt)
                
                cv2.imshow("camera", img_rd)
                if liveness.check(frame_cnt=self.frame_cnt): # 活体检测通过
                    self.write_log_to_file(img_rd, stat='success')
                    return True
                elif face_timer > 233: # 目标脸一直没出现
                    self.write_log_to_file(img_rd, stat='failed with long time no target face')
                    return False
                if time.time() - start_time > 30: # 30s超时
                    self.write_log_to_file(img_rd, stat='failed with time out')
                    return False                
                # 按下 q 键退出 / Press 'q' to quit
                if kk == ord('q'):
                    self.write_log_to_file(img_rd, stat='failed with press q')
                    break

                # 9. 更新 FPS / Update stream FPS
                self.update_fps()
                logging.debug("Frame ends\n\n")
        else:
            logging.warning("Can't find this person in face database")
            return False
        
    def run(self):
        # cap = cv2.VideoCapture("video.mp4")  # Get video stream from video file
        cap = cv2.VideoCapture(0)              # Get video stream from camera
        res = self.process(cap)

        cap.release()
        cv2.destroyAllWindows()
        
        return res

# if __name__ == '__main__':
#     name = 'Heng Li'
#     face_reco = Face_Recognizer(name)
#     flg = face_reco.process(cv2.VideoCapture(0))
#     if flg == True:
#         print(f'welcome {face_reco.name}')