from collections import OrderedDict
import lmdb
import sys
import json
import Log

class Conlmdb():
    """
    建立操作的lmdb的相关接口
    包括：
    connect连接
    put插入
    delete删除
    get取值
    exist判断存在
    set重新设置
    dbsize获得大小
    drop删除
    iter遍历
    """
    def __init__(self,name="wallet"):
        try:
            self.conn = self.connect(name)
        except Exception as e:
            Log.Error("连接数据库失败！")
            sys.exit()


    def connect(self,name):
        #建立连接操作
        return lmdb.open(name)


    def encode(self,string):
        #对字符串进行严格的编码
        #注意，这里不能多次编码
        if type(string) == type("string"):
            return string.encode("utf-8")
        elif type(string) == type(b"string"):
            return string
        else:
            return str(string).encode("utf-8")


    def decode(self,string):
        #对字符串进行解码
        return string.decode("utf-8")


    def put(self,key,value):
        #插入操作
        key = self.encode(key)
        value = self.encode(value)
        txn = self.conn.begin(write=True)
        txn.put(key,value)
        txn.commit()


    def delete(self,key):
        #删除键值对
        key = self.encode(key)
        txn = self.conn.begin(write=True)
        txn.delete(key)
        txn.commit()


    def get(self,key):
        #查找某个键对应的值
        key = self.encode(key)
        txn = self.conn.begin()
        value = txn.get(key)
        result=self.decode(value) if value else None
        txn.commit()
        return result


    def exist(self,key):
        #判断键值对是否存在
        return True if self.get(key) else False


    def set(self,key,value):
        key = self.encode(key)
        value = self.encode(value)
        #如果某个键值对存在则更新值
        txn = self.conn.begin(write=True)
        if self.exist(key):
            txn.put(self.encode(key),value)
        else:
            pass
        txn.commit()


    def dbsize(self):
        #数据条数
        txn = self.conn.begin()
        size = txn.stat()["entries"]
        txn.commit()
        return size


    def drop(self):
        #丢弃数据库所有内容
        txn = self.conn.begin()
        for key,value in txn.cursor():
           self.delete(self.decode(key))


    def iter(self,tip="l",goal="None"):
        #按序遍历数据库内容，也可以作为检查依据,返回带有顺序的数据库内容
        tip = self.get(tip)
        temp = OrderedDict()
        result = OrderedDict()
        while tip!=goal:
            data = self.get(tip)
            if data:
                temp[tip]=data
                tip = json.loads(data.replace("'",'"'))["Headers"]["PrevBlockHash"]
            else:
                tip=goal
        for key in reversed(temp):
            result[key] = temp[key]
        return result



    def rawiter(self):
        #返回原生的数据库内容
        txn = self.conn.begin()
        result = dict()
        for key,value in txn.cursor():
            if key.decode("utf-8") != "l":
                result[key] = value
        txn.commit()
        return result


    def close(self):
        #关闭连接
        self.conn.close()
