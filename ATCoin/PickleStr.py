import pickle

"""
写入数据库序列化与读出数据反序列化
"""
def toStr(object):
    #写入数据序列化为list字符串
    return str(list(pickle.dumps(object)))


def toObj(string):
    #读出数据反序列化为对象
    if type(string) != type("a"):
        string = string.decode("utf-8")
    result = string.replace("[", "").replace("]", "").split(",")
    for i in range(len(result)):
        result[i] = int(result[i])
    test = pickle.loads(bytearray(result))
    return test
