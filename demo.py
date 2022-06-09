import csv
import os
import re
import shutil
import threading
import tkinter
import datetime
from tkinter import messagebox
from difflib import Differ
from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter.ttk import Progressbar
import configparser

from PIL._imagingmorph import apply

"""
@author:碎水
@qq:562000490
@WeChat:whosdead
"""

kaohao = 11

word = 3.0
punctuation = 0.5

Total = {}
wordsNum = {}
Error = {}
errorFileList = []
pathDict = {"docu": os.getcwd() + "\\参赛者打字内容",
            "ans": os.getcwd() + "\\试卷答案"
            }


class MultiListbox(Frame):
    def __init__(self, master, lists):
        Frame.__init__(self, master)
        self.lists = []
        for l, w in lists:
            frame = Frame(self)
            frame.pack(side=LEFT, expand=YES, fill=BOTH)
            Label(frame, text=l, borderwidth=1, relief=RAISED).pack(fill=X)
            lb = Listbox(frame, width=w, borderwidth=0, selectborderwidth=0, relief=FLAT, exportselection=FALSE)
            lb.pack(expand=YES, fill=BOTH)
            self.lists.append(lb)
            lb.bind("<B1-Motion>", lambda e, s=self: s._select(e.y))
            lb.bind("<Button-1>", lambda e, s=self: s._select(e.y))
            lb.bind("<Leave>", lambda e: "break")
            lb.bind("<B2-Motion>", lambda e, s=self: s._b2motion(e.x, e.y))
            lb.bind("<Button-2>", lambda e, s=self: s._button2(e.x, e.y))
        frame = Frame(self)
        frame.pack(side=LEFT, fill=Y)
        Label(frame, borderwidth=1, relief=RAISED).pack(fill=X)
        sb = Scrollbar(frame, orient=VERTICAL, command=self._scroll)
        sb.pack(side=LEFT, fill=Y)
        self.lists[0]["yscrollcommand"] = sb.set

    def _select(self, y):
        row = self.lists[0].nearest(y)
        self.selection_clear(0, END)
        self.selection_set(row)
        return "break"

    def _button2(self, x, y):
        for l in self.lists:
            l.scan_mark(x, y)
        return "break"

    def _b2motion(self, x, y):
        for l in self.lists:
            l.scan_dragto(x, y)
        return "break"

    def _scroll(self, *args):
        for l in self.lists:
            apply(l.yview, args)
        return "break"

    def curselection(self):
        return self.lists[0].curselection()

    def delete(self, first, last=None):
        for l in self.lists:
            l.delete(first, last)

    def get(self, first, last=None):
        result = []
        for l in self.lists:
            result.append(l.get(first, last))
        if last:
            return apply(map, [None] + result)
        return result

    def index(self, index):
        self.lists[0], index(index)

    def insert(self, index, *elements):
        for e in elements:
            i = 0
            for l in self.lists:
                l.insert(index, e[i])
                i = i + 1

    def size(self):
        return self.lists[0].size()

    def see(self, index):
        for l in self.lists:
            l.see(index)

    def selection_anchor(self, index):
        for l in self.lists:
            l.selection_anchor(index)

    def selection_clear(self, first, last=None):
        for l in self.lists:
            l.selection_clear(first, last)

    def selection_includes(self, index):
        return self.lists[0].seleciton_includes(index)

    def selection_set(self, first, last=None):
        for l in self.lists:
            l.selection_set(first, last)


def setDir(Type):

    path1 = askdirectory()

    if path1 != '':
        pathDict[Type[0]] = path1
        conf.set("sets",Type[0],path1.split("/")[-1])
        conf.write(open("conf.ini", "w", encoding="utf-8"))
        if Type[0]=="docu":
            dirText1.delete(0, END)
            dirText1.insert(tkinter.INSERT, pathDict["docu"])
        elif Type[0]=="ans":
            dirText2.delete(0, END)
            dirText2.insert(tkinter.INSERT, pathDict["ans"])


def getDir(Type):
    return pathDict[Type]


def readList(Path):
    return os.listdir(Path)


def readFile(filename):
    with open(getDir("docu") + "\\" + filename, 'r', encoding="UTF-8") as f:
        return f.read()


def getAnswer(num):
    with open(getDir("ans") + "\\" + num + ".txt", 'r', encoding="UTF-8") as f:
        return f.read()


def judge(str):
    global word, punctuation
    if '\u4e00' <= str <= '\u9fff':
        return [word,"word"]
    else:
        return [punctuation,"punctuation"]


def strCompare(str, answer, key):
    try:
        str = str.replace(' ', '')
        answer = answer.replace(' ', '')
        str = str.replace('\n', '')
        answer = answer.replace('\n', '')
        str = str.replace('\r', '')
        answer = answer.replace('\r', '')
        str = str.replace('\t', '')
        answer = answer.replace('\t', '')
        score = len(answer)
        wordsNum[key] = score
        score1 = score
        lackList = []
        noList = []
        errorList = []
        errorWordCount = 0
        errorpCount = 0
        d = Differ()
        diff = d.compare(answer.splitlines(), str.splitlines())
        str0 = ''.join(list(diff))
        if len(str0) == score + 2:
            Error[key] = [errorList, lackList, noList, errorWordCount, errorpCount]
            return score
        if str0.find("+") != -1 and str0.find("?") != -1:
            ans = str0[len(answer) + 4:str0.find("+")]
            str1 = str0[str0.find("+") + len(str) + 4:]
        else:
            if str0.find("+") != -1 and str0.find("-") != -1:
                Error[key] = ["*", "*", "*", "*", "*"]
                return 0
            else:
                Error[key] = [errorList, lackList, noList, errorWordCount, errorpCount]
                return score
        for s in range(len(str1)):
            if str1[s] == "+":
                noList.append(str[s])
                delta = judge(str[s])
                score1 -= delta[0]
                if delta[1] == "word":
                    errorWordCount += 1
                else:
                    errorpCount += 1
        for a in range(len(ans)):
            if ans[a] == "^":
                errorList.append(answer[a])
                delta = judge(answer[a])
                score1 -= delta[0]
                if delta[1] == "word":
                    errorWordCount += 1
                else:
                    errorpCount += 1
            elif ans[a] == "-":
                lackList.append(answer[a])
                delta = judge(answer[a])
                score1 -= delta[0]
                if delta[1] == "word":
                    errorWordCount += 1
                else:
                    errorpCount += 1

        Error[key] = [errorList, lackList, noList, errorWordCount, errorpCount]
        if score1 < 0:
            score1 = 0
        return (score1 if (score1 - int(score1)) else int(score1))
    except:
        return 0


def mainFunction(filename):
    global point
    try:

        key = filename.replace('.txt', '')
        pattern = re.compile(r'\d+')
        result1 = pattern.findall(key[:2])
        result2 = pattern.findall(key[-kaohao:])
        if len(result1[0]) == 2 and len(result2[0]) == kaohao:
            if key[:2] + ".txt" in readList(pathDict["ans"]):
                Total[key] = strCompare(readFile(filename), getAnswer(filename[:2]), key)
            else:
                shutil.move(pathDict['docu'] + "\\" + filename, os.getcwd() + "\\命名错误")

                errorFileList.append("试卷{}命名错误".format(key))
        else:
            shutil.move(pathDict['docu'] + "\\" + filename, os.getcwd() + "\\命名错误")

            errorFileList.append("试卷{}命名错误".format(key))
        p1["value"] += 1

        frame11.update()

    except FileNotFoundError:
        messagebox.showinfo("提示", "找不到指定路径或文件")
    except:
        return


def pathFileIsexist(uFilepath, uFolder):
    if os.path.exists(os.path.join(uFolder, uFilepath.split('\\')[-1])):  # 目标文件夹+要移动的文件名
        newFilepath = '{0}_{1}.{2}'.format(uFilepath.split('.')[0], datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
                                           uFilepath.split('.')[-1])  # 存在,则切割成:原文件路径(不带格式)_时间戳.原文件格式
        os.rename(uFilepath, newFilepath)  # 重命名
        return newFilepath  # 返回新文件路径
    else:
        return uFilepath  # 不重复,返回原路径


def christen():
    try:
        flag = 0
        fileList = readList(getDir("docu"))
        for filename in fileList:
            key = filename.replace('.txt', '')
            pattern = re.compile(r'\d+')
            result1 = pattern.findall(key[:2])
            result2 = pattern.findall(key[-kaohao:])
            if len(result1[0]) == 2 and len(result2[0]) == kaohao:
                if key[:2] + ".txt" in readList(pathDict["ans"]):
                    continue
                else:
                    shutil.move(pathFileIsexist(pathDict['docu'] + "\\" + filename, os.getcwd() + "\\命名错误"),
                                os.getcwd() + "\\命名错误")
                    errorFileList.append("试卷“{}”命名错误".format(key))
                    flag = 1
            else:
                # shutil.move(pathDict['docu'] + "\\" + filename, os.getcwd() + "\\命名错误")
                shutil.move(pathFileIsexist(pathDict['docu'] + "\\" + filename, os.getcwd() + "\\命名错误"),
                            os.getcwd() + "\\命名错误")
                errorFileList.append("试卷“{}”命名错误".format(key))

                flag = 1
        if flag == 1:
            f = open("错误命名.txt", 'w', encoding="UTF-8")
            for error in errorFileList:
                f.write(error + "\n")
            f.close()

        return flag

    except FileNotFoundError:
        messagebox.showinfo("提示", "找不到指定路径或文件")
    except:
        return


def start():
    try:
        thread = []
        with open('评分结果.csv', 'w', newline='') as csvfile:
            pass
        fileList = readList(getDir("docu"))
        for i in range(len(fileList)):
            try:
                t = threading.Thread(target=mainFunction, args=(fileList[i],))
                t.start()
                thread.append(t)
                if i % 4 == 3:
                    for th in thread:
                        th.join()
                        thread.remove(th)
                frame11.update()
            except:
                continue
        for t in thread:
            t.join()
        frame11.update()
        with open('评分结果.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile)
            spamwriter.writerow(["题库", "选手", "考号", "总字数", "错字", "漏字", "多字", "错误汉字数", "错误标点数", "成绩"])
            for key, value in Total.items():
                spamwriter.writerow(
                    [key[0:2], key[2:-kaohao], key[-kaohao:], wordsNum[key],
                     "\"{}\"".format("\",\"".join(Error[key][0])) if len(Error[key][0]) != 0 else "",
                     "\"{}\"".format("\",\"".join(Error[key][1])) if len(Error[key][1]) != 0 else "",
                     "\"{}\"".format("\",\"".join(Error[key][2])) if len(Error[key][2]) != 0 else "", Error[key][3],
                     Error[key][4],
                     value])
                mlb.insert(END, (key[0:2], key[-kaohao:], key[2:-kaohao], value, wordsNum[key]))

        Total.clear()
        wordsNum.clear()
        Error.clear()
        errorFileList.clear()
        mlb.pack(expand=YES, fill=BOTH)
        p1["value"] = len(readList(getDir("docu")))

        frame11.update()
    except PermissionError:
        messagebox.showinfo("提示", "评分结果.csv被占用")


def init():
    global word, punctuation

    p1["value"] = 0
    conf.set("sets","word",wordText.get())
    conf.set("sets","punctuation",pText.get())
    conf.write(open("conf.ini", "w", encoding="utf-8"))

    word = float(wordText.get())
    punctuation = float(pText.get())

    if christen() == 1:
        askback = messagebox.askyesno('温馨提示', '出现命名错误，是否继续评分?')
        if askback == True:
            threading.Thread(target=start).start()
        else:
            pass
    else:
        threading.Thread(target=start).start()


def parameterInit():
    global word, punctuation, kaohao

    pathDict["docu"] = os.getcwd() + "\\" + conf.get("sets", "docu")
    pathDict["ans"] = os.getcwd() + "\\" + conf.get("sets", "ans")
    word = float(conf.get("sets", "word"))
    punctuation = float(conf.get("sets", "punctuation"))
    kaohao = int(conf.get("sets", "numberDigits"))


if __name__ == '__main__':

    try:
        try:
            os.mkdir("命名错误")
        except FileExistsError:
            pass
        try:
            os.mkdir("试卷答案")
        except FileExistsError:
            pass
        try:
            os.mkdir("参赛者打字内容")
        except FileExistsError:
            pass
        conf = configparser.ConfigParser()
        conf.read("conf.ini", encoding="utf-8")
        parameterInit()
        top = tkinter.Tk()
        top.title("打字评分")
        top.geometry('400x600')
        top.resizable(0, 0)
        frame1 = tkinter.Frame(top)
        frame1.pack(side='top', fill=tkinter.X, anchor='nw')
        tkinter.Label(frame1, text="考卷文件夹路径:").grid(row=4, column=1, sticky='w')
        tkinter.Label(frame1, text="答案文件夹路径:").grid(row=6, column=1, sticky='w')
        setDirButton = tkinter.Button(frame1, text="更改考卷文件夹", command=lambda: setDir(("docu",)))
        setDirButton.grid(row=4, column=4, sticky='e')
        getDirButton = tkinter.Button(frame1, text="更改答案文件夹", command=lambda: setDir(("ans",)))
        getDirButton.grid(row=6, column=4, sticky='e')
        dirText1 = tkinter.Entry(frame1, width=56)
        dirText1.insert(tkinter.INSERT, pathDict["docu"])
        dirText1.grid(row=5, column=1, columnspan=4)
        dirText2 = tkinter.Entry(frame1, width=56)
        dirText2.insert(tkinter.INSERT, pathDict["ans"])
        dirText2.grid(row=7, column=1, columnspan=4)

        tkinter.Label(frame1, text="     单字计分:").grid(row=2, column=1, sticky='w')
        tkinter.Label(frame1, text="     标点计分:").grid(row=2, column=3, sticky='w')
        wordText = tkinter.Entry(frame1, width=13)
        wordText.insert(tkinter.INSERT, word)
        wordText.grid(row=2, column=2, columnspan=1)
        pText = tkinter.Entry(frame1, width=13)
        pText.insert(tkinter.INSERT, punctuation)
        pText.grid(row=2, column=4, columnspan=1)
        onButton = tkinter.Button(frame1, text="开启计算", command=init, width=12).grid(row=1, column=4, sticky='e')
        frame11 = tkinter.Frame(frame1)
        frame11.grid(row=1, column=1, sticky='w', columnspan=3)
        p1 = Progressbar(frame11, length=300, cursor='spider',
                         mode="determinate",
                         orient=tkinter.HORIZONTAL,
                         maximum=len(readList(getDir("docu"))),
                         )
        p1.grid(row=1, column=1, sticky='e')
        frame2 = tkinter.Frame(top)
        frame2.pack(side='top', fill=tkinter.X, anchor='nw')
        mlb = MultiListbox(frame2, (('试卷号', 5), ('考号', 10), ("姓名", 10), ('得分', 10), ('满分', 10)))
        top.mainloop()
    except FileNotFoundError:
        messagebox.showinfo("提示", "找不到指定路径或文件")
    except:
        messagebox.showinfo("提示", "未知错误")