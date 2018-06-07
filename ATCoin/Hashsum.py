import hashlib
import Log

"""
数字货币使用到的单向加密函数
1.SHA256加密字符串
2.Ripemd160加密字符串
"""


def Enhash(data):
    try:
        if type(data) == type("s"):
            data = data.encode("utf-8")
        elif type(data) != type(b"1"):#排除本身就是bytes类型的情况，这样就不用在进行编码
            data = str(data).encode("utf-8")
        result = hashlib.sha256(data).hexdigest()
        return result
    except Exception as e:
        Log.Error(e)
        print("sha256加密出错：",e)


def Ripemd160(data):
    try:
        if type(data) == type("s"):
            data = data.encode("utf-8")
        elif type(data) != type(b"1"):
            data = str(data).encode("utf-8")
        result = hashlib.new('ripemd160',data).hexdigest()
        return result
    except Exception as e:
        Log.Error(e)
        print("Ripemd加密出错：",e)

