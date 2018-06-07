import json

def toJson(string):
    """
    :json字符串转化为字典
    :return:
    """
    string = str(string).replace("'",'"').replace("'{","{").replace("}'","}").replace("\"{","{").replace("}\"","}")
    return json.loads(string)


def toStr(sjson):
    """
    :字典转化为json字符串
    :return:
    """
    return json.dumps(sjson)
