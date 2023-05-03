from tkinter import *
from tkinter.ttk import *
from db import *
from metaData import *
import logging
import loginPage
import registerPage
import resultPage 
import get_faces_from_camera_tkinter2 as get_face
# import face_reco_from_camera_ot2 as face_reco
import face_reco_from_camera_with_name as face_reco


# 包装层
class Face_Rigister_Tk(get_face.Face_Register):
    def __init__(self, username):
        super().__init__(username)

class Face_Recognizer_Tk(face_reco.Face_Recognizer):
    def __init__(self, username):
        super().__init__(username)


def main():
    # metaData
    metaData  = MetaData()
    metaData.step2WinName = 'login'
    logging.basicConfig(level=logging.INFO)

    # 主循环: 用个自动机
    while True:
        if metaData.step2WinName == 'exit':
            break

        elif metaData.step2WinName == 'login':
            win = loginPage.Win(metaData)
            win.mainloop()
            logging.debug(f'username: {metaData.username}')
            logging.debug(f'password: {metaData.password}')
            
        elif metaData.step2WinName == 'register':
            win = registerPage.Win(metaData)
            win.mainloop()
            logging.debug(f'username: {metaData.username}')
            logging.debug(f'password: {metaData.password}')

        elif metaData.step2WinName == 'judgeInputLogin':
            # 先检查输入合法性
            if metaData.username == "" or metaData.password == "":
                metaData.information = "登录的用户名或密码不能为空"
                metaData.step2WinName = 'resultAndGotoLogin'
                continue
            # 再检查用户名密码
            db = DB('system.db')
            rows = db.select(metaData.username, metaData.password)
            if len(rows) == 0:
                metaData.information = "用户名或密码错误"
                metaData.step2WinName = 'resultAndGotoLogin'
                continue
            # 最后没问题就进入人脸识别
            metaData.step2WinName = 'faceReco'
        
        elif metaData.step2WinName == 'judgeInputRegister':
            # 先检查输入合法性
            if metaData.username == "" or metaData.password == "":
                metaData.information = "注册的用户名或密码不能为空"
                metaData.step2WinName = 'resultAndGotoLogin'
                continue
            # 再检查用户名是否重复
            db = DB('system.db')
            rows = db.selectByUsername(metaData.username)
            if len(rows) > 0:
                metaData.information = "用户名已存在"
                metaData.step2WinName = 'resultAndGotoLogin'
                continue
            # 最后没问题就进入人脸采集
            metaData.step2WinName = 'getFace'

        elif metaData.step2WinName == 'faceReco':
            # 人脸识别
            Face_Recognizer_con = Face_Recognizer_Tk(metaData.username)
            result = Face_Recognizer_con.run()
            # 查看结果
            if result:
                metaData.information = "登录成功"
                metaData.step2WinName = 'resultAndGotoSystem'
            else:
                metaData.information = "登录失败: 人脸识别不匹配"
                metaData.step2WinName = 'resultAndGotoLogin'

        elif metaData.step2WinName == 'getFace':
            # 人脸录入
            Face_Register_con = Face_Rigister_Tk(metaData.username)
            result = Face_Register_con.run()
            # 查看结果
            if result:
                metaData.information = "注册成功"
                db.insert(metaData.username, metaData.password)
            else:
                metaData.information = "人脸注册失败: 人脸信息获取失败"
            # 什么结果都是回登录页
            metaData.step2WinName = 'resultAndGotoLogin'

        elif metaData.step2WinName == 'resultAndGotoLogin':
            logging.info(metaData.information)
            resultWin = resultPage.Win(metaData.information)
            resultWin.mainloop()
            metaData.step2WinName = 'login' # 重新去登录页

        elif metaData.step2WinName == 'resultAndGotoSystem':
            logging.info(metaData.information)
            resultWin = resultPage.Win(metaData.information)
            resultWin.mainloop()
            metaData.step2WinName = 'systemPage' # 重新去登录页

        elif metaData.step2WinName == 'systemPage':
            resultWin = resultPage.Win("该页面为内部系统页面")
            resultWin.mainloop()
            metaData.step2WinName = 'exit' # 结束

        else:
            metaData.information = "出现错误: 未知的step2WinName"
            metaData.step2WinName = 'resultAndGotoLogin'


if __name__ == "__main__":
    main()