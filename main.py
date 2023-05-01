from tkinter import *
from tkinter.ttk import *
from typing import Dict
import logging
import sqlite3
import get_faces_from_camera_tkinter2 as get_face
import face_reco_from_camera_ot2 as face_reco
# import face_reco_from_camera_with_name as face_reco


# 全局量
class MetaData:
    def __init__(self) -> None:
        username = ''
        password = ''
        step2WinName = ''
        result = 0 # 0: 失败 1: 成功
        information = ''


# 入口布局
class WinGUI(Tk):
    widget_dic: Dict[str, Widget] = {}

    def __init__(self):
        super().__init__()
        self.__win()
        self.widget_dic["tk_input_username_input"] = self.__tk_input_username_input(
            self)
        self.widget_dic["tk_input_password_input"] = self.__tk_input_password_input(
            self)
        self.widget_dic["tk_label_password_label"] = self.__tk_label_password_label(
            self)
        self.widget_dic["tk_label_username_label"] = self.__tk_label_username_label(
            self)
        self.widget_dic["tk_button_register_button"] = self.__tk_button_register_button(
            self)
        self.widget_dic["tk_button_login_button"] = self.__tk_button_login_button(
            self)
        self.widget_dic["tk_label_title"] = self.__tk_label_title(self)

    def __win(self):
        self.title("内部系统")
        # 设置窗口大小、居中
        width = 591
        height = 422
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height,
                                    (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)
        self.resizable(width=False, height=False)

        # 自动隐藏滚动条
    def scrollbar_autohide(self, bar, widget):
        self.__scrollbar_hide(bar, widget)
        widget.bind("<Enter>", lambda e: self.__scrollbar_show(bar, widget))
        bar.bind("<Enter>", lambda e: self.__scrollbar_show(bar, widget))
        widget.bind("<Leave>", lambda e: self.__scrollbar_hide(bar, widget))
        bar.bind("<Leave>", lambda e: self.__scrollbar_hide(bar, widget))

    def __scrollbar_show(self, bar, widget):
        bar.lift(widget)

    def __scrollbar_hide(self, bar, widget):
        bar.lower(widget)

    def __tk_input_username_input(self, parent):
        ipt = Entry(parent)
        ipt.place(x=230, y=160, width=199, height=40)
        return ipt

    def __tk_input_password_input(self, parent):
        ipt = Entry(parent)
        ipt.place(x=230, y=240, width=199, height=38)
        return ipt

    def __tk_label_password_label(self, parent):
        label = Label(parent, text="密码", anchor="center")
        label.place(x=120, y=240, width=87, height=41)
        return label

    def __tk_label_username_label(self, parent):
        label = Label(parent, text="用户名", anchor="center")
        label.place(x=120, y=160, width=87, height=41)
        return label

    def __tk_button_register_button(self, parent):
        btn = Button(parent, text="注册")
        btn.place(x=170, y=330, width=104, height=44)
        return btn

    def __tk_button_login_button(self, parent):
        btn = Button(parent, text="登录")
        btn.place(x=300, y=330, width=104, height=44)
        return btn

    def __tk_label_title(self, parent):
        label = Label(parent, text="系统入口", anchor="center")
        label.place(x=145, y=24, width=278, height=98)
        return label


# 入口行为
class Win(WinGUI):
    def __init__(self, metaData:MetaData):
        super().__init__()
        self.metaData = metaData
        self.__event_bind()

    def register(self, evt):
        global step2WinName
        logging.info("Win - register事件")
        self.printInput()
        self.getInput()
        step2WinName = "registerWin"
        self.destroy()
        

    def login(self, evt):
        global step2WinName
        print("Win - login事件")
        self.printInput()
        self.getInput()
        step2WinName = "loginWin"
        self.destroy()

    def __event_bind(self):
        self.widget_dic["tk_button_register_button"].bind(
            '<Button-1>', self.register)
        self.widget_dic["tk_button_login_button"].bind(
            '<Button-1>', self.login)

    # utils methond
    def getUsername(self):
        return self.widget_dic["tk_input_username_input"].get()

    def getPassword(self):
        return self.widget_dic["tk_input_password_input"].get()

    def printInput(self):
        print(f'username: {self.getUsername()}')
        print(f'password: {self.getPassword()}')
    
    def getInput(self):
        self.metaData.username = self.getUsername()
        self.metaData.password = self.getPassword()


# result布局
class ResultWinGUI(Tk):
    widget_dic: Dict[str, Widget] = {}
    def __init__(self, information):
        self.information = information
        super().__init__()
        self.__win()
        self.widget_dic["tk_label_result_label"] = self.__tk_label_result_label(self)
        self.widget_dic["tk_button_ok_button"] = self.__tk_button_ok_button(self)

    def __win(self):
        self.title(self.information)
        # 设置窗口大小、居中
        width = 435
        height = 267
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)
        self.resizable(width=False, height=False)

        # 自动隐藏滚动条
    def scrollbar_autohide(self,bar,widget):
        self.__scrollbar_hide(bar,widget)
        widget.bind("<Enter>", lambda e: self.__scrollbar_show(bar,widget))
        bar.bind("<Enter>", lambda e: self.__scrollbar_show(bar,widget))
        widget.bind("<Leave>", lambda e: self.__scrollbar_hide(bar,widget))
        bar.bind("<Leave>", lambda e: self.__scrollbar_hide(bar,widget))
    
    def __scrollbar_show(self,bar,widget):
        bar.lift(widget)

    def __scrollbar_hide(self,bar,widget):
        bar.lower(widget)
        
    def __tk_label_result_label(self,parent):
        label = Label(parent,text=self.information,anchor="center")
        label.place(x=0, y=2, width=432, height=165)
        return label

    def __tk_button_ok_button(self,parent):
        btn = Button(parent, text="确定")
        btn.place(x=200, y=200, width=50, height=30)
        return btn


# result行为
class ResultWin(ResultWinGUI):
    def __init__(self, information):
        super().__init__(information)
        self.__event_bind()

    def OK(self,evt):
        print("ResultWin - OK 事件",evt)
        self.destroy()
        
    def __event_bind(self):
        self.widget_dic["tk_button_ok_button"].bind('<Button-1>',self.OK)


# 包装层
class Face_Rigister_Tk(get_face.Face_Register):
    def __init__(self, username):
        super().__init__(username)

class Face_Recognizer_Tk(face_reco.Face_Recognizer):
    def __init__(self, username):
        super().__init__(username)


# db操作
class DB:
    def __init__(self, file):
        # 连接数据库
        self.conn = sqlite3.connect(file)
        logging.info("Opened database successfully")

        # 创建 user 表
        self.conn.execute('''
        CREATE TABLE  IF NOT EXISTS user(
            id INTEGER primary key AUTOINCREMENT,
            username text,
            password text
        )
        ''')

    def insert(self, username, password):
        self.conn.execute(f'''
        INSERT INTO user (username, password) VALUES ('{username}', '{password}')
        ''')
        self.conn.commit()
        logging.info("Records created successfully")
    
    def select(self, username, password):
        cursor = self.conn.execute(f'''
        SELECT * FROM user WHERE username = '{username}' AND password = '{password}'
        ''')
        return cursor.fetchall()
    
    def selectByUsername(self, username):
        cursor = self.conn.execute(f'''
        SELECT * FROM user WHERE username = '{username}'
        ''')
        return cursor.fetchall()


def bussiness(metaData):
    # 连接数据库
    db = DB('system.db')
    rows = db.selectByUsername(metaData.username)

    if step2WinName == "registerWin":
        # 用户名重复不给注册
        if len(rows) > 0:
            information = "用户名已存在"
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

    elif step2WinName == "loginWin":
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
    # 初始化日志
    logging.basicConfig(level=logging.INFO)

    # metaData
    metaData  = MetaData()

    # 入口
    win = Win(metaData)
    win.mainloop()
    logging.debug(f'username: {metaData.username}')
    logging.debug(f'password: {metaData.password}')

    # 检查输入合法性
    if metaData.username == "" or metaData.password == "":
        logging.info("用户名或密码不能为空")
        resultWin = ResultWin("用户名或密码不能为空")
        resultWin.mainloop()
        exit(0)

    # 业务逻辑: register or login
    bussiness(metaData)
    
    # 输出结果
    logging.info(metaData.information)
    resultWin = ResultWin(metaData.information)
    resultWin.mainloop()


if __name__ == "__main__":
    main()