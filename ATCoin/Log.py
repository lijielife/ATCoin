import time
import os


"""
处理日志记录
"""
time = time.asctime(time.localtime())


def Panic(data):
    try:
        with open("logs/panic.log","a",encoding="utf-8") as fo:
            fo.write(os.linesep)
            fo.write(time)
            fo.write(" "+str(data))
    except Exception as e:
        print(e)


def Error(data):
    try:
        with open("logs/error.log","a",encoding="utf-8") as fo:
            fo.write(os.linesep)
            fo.write(time)
            fo.write(" "+str(data))
    except Exception as e:
        print(e)


def Access(data):
    """
    记录登陆信息日志
    :param data: 登录信息
    """
    try:
        with open("logs/access.log","a",encoding="utf-8") as fo:
            fo.write(os.linesep)
            fo.write(time)
            fo.write(" "+str(data))
    except Exception as e:
        print(e)