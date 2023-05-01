from tkinter import *
from tkinter.ttk import *
from db import *
from metaData import *
from result import *
import logging
import login
import register
import get_faces_from_camera_tkinter2 as get_face
import face_reco_from_camera_ot2 as face_reco
# import face_reco_from_camera_with_name as face_reco


# 包装层
class Face_Rigister_Tk(get_face.Face_Register):
    def __init__(self, username):
        super().__init__(username)

class Face_Recognizer_Tk(face_reco.Face_Recognizer):
    def __init__(self, username):
        super().__init__(username)


def bussiness(metaData: MetaData):
    # 连接数据库
    db = DB('system.db')
    rows = db.selectByUsername(metaData.username)

    if metaData.step2WinName == "registerWin":
        # 用户名重复不给注册
        if len(rows) > 0:
            metaData.information = "用户名已存在"
            return
        
        # 人脸录入
        Face_Register_con = Face_Rigister_Tk(metaData.username)
        result = Face_Register_con.run()

        # 查看结果
        if result:
            metaData.information = "注册成功"
            db.insert(metaData.username, metaData.password)
        else:
            metaData.information = "注册失败"

    elif metaData.step2WinName == "loginWin":
        # 检查用户名密码
        rows = db.select(metaData.username, metaData.password)
        if len(rows) == 0:
            metaData.information = "用户名或密码错误"
            return

        # 人脸识别
        Face_Recognizer_con = Face_Recognizer_Tk(metaData.username)
        result = Face_Recognizer_con.run()

        # 查看结果
        if result:
            metaData.information = "登录成功"
        else:
            metaData.information = "登录失败"
    else:
        # 不明情况
        metaData.information = "出现错误: 未知的step2WinName"


def main():
    # metaData
    metaData  = MetaData()
    logging.basicConfig(level=logging.INFO)

    # 主循环
    while not metaData.close:
        # 入口
        win = login.Win(metaData)
        win.mainloop()
        logging.debug(f'username: {metaData.username}')
        logging.debug(f'password: {metaData.password}')

        # 检查输入合法性
        if metaData.username == "" or metaData.password == "":
            logging.info("用户名或密码不能为空")
            resultWin = ResultWin("用户名或密码不能为空")
            resultWin.mainloop()
            continue

        # 业务逻辑: register or login
        bussiness(metaData)
        
        # 输出结果
        logging.info(metaData.information)
        resultWin = ResultWin(metaData.information)
        resultWin.mainloop()


if __name__ == "__main__":
    main()