from tkinter import *
from tkinter.ttk import *
from typing import Dict
from metaData import *

# result布局
class WinGUI(Tk):
    widget_dic: Dict[str, Widget] = {}
    information = ""

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
class Win(WinGUI):
    def __init__(self, information):
        super().__init__(information)
        self.__event_bind()

    def OK(self,evt):
        print("ResultWin - OK 事件",evt)
        self.destroy()
        
    def __event_bind(self):
        self.widget_dic["tk_button_ok_button"].bind('<Button-1>',self.OK)