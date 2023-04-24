from tkinter import *
from tkinter.ttk import *
from typing import Dict
import logging
import get_faces_from_camera_tkinter
import face_reco_from_camera_ot

# 全局量
username = ''
password = ''
step2WinName = ''
result = ''

# 布局
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

# 行为
class Win(WinGUI):
    def __init__(self):
        super().__init__()
        self.__event_bind()

    def register(self, evt):
        global step2WinName
        logging.info("调用register", evt)
        self.printInput()
        self.getInput()
        step2WinName = "registerWin"
        self.destroy()
        

    def login(self, evt):
        global step2WinName
        print("调用login", evt)
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
        global username, password
        username = self.getUsername()
        password = self.getPassword()

# 包装层
class Face_Rigister_Tk(get_faces_from_camera_tkinter.Face_Register):
    def __init__(self):
        super().__init__()

class Face_Recognizer_Tk(face_reco_from_camera_ot.Face_Recognizer):
    def __init__(self):
        super().__init__()

    


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # 入口
    win = Win()
    win.mainloop()

    # 检查输入合法性

    # 人脸识别
    if step2WinName == "registerWin":
        Face_Register_con = Face_Rigister_Tk()
        Face_Register_con.run()
    elif step2WinName == "loginWin":
        Face_Recognizer_con = Face_Recognizer_Tk()
        Face_Recognizer_con.run()
    else:
        logging.info("未知的step2WinName")

    # 结果


    print(f'username: {username}')
    print(f'password: {password}')
