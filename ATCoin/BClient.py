from twisted.internet import protocol,reactor
from Utils import Utils
from Communicate import SendMsg
from Conlmdb import Conlmdb
from Blockchain import Blockchain
from queue import Queue
import Jsonstr
import Log
import Server
import DataProcess
import sys


pid = Queue()
class dealData:
    def storeData(self,data):
        result = True
        db = Conlmdb()
        try:
            dbmap = Jsonstr.toJson(data)
            db.delete("l")
            p = pid.get()
            for value in dbmap.values():
                upb = Blockchain().updateblock(value,p)
                if upb == "restart":
                    result = "restart"
                elif upb:
                    result =True
                else:

                    return False
        except Exception as e:
            print("Json解析出错：BClient中第20行处解析出错，有可能是传输区块没有完成")
            Log.Error("Json解析出错：BClient中第20行处解析出错，有可能是传输区块没有完成")

        return result



class TSClntProtocol(protocol.Protocol):
    """
    区块链之间的同步
    """
    _data_buffer = ""
    def sendData(self,data):
        if data:
            print("...sending "+data+"...")
            if type(data) == type("s"):
                data = data.encode("utf-8")
            self.transport.write(data+b"Finsh")
        else:
            self.transport.loseConnection()


    def connectionMade(self):
        obj = SendMsg()
        data = "Initialization"+"|"+obj.version+"|"+obj.BestHeight+"|"+obj.Cblock+"|"+obj.ipaddr
        self.sendData(data)


    def dataReceived(self,data):
        if data:
            content = data.decode("utf-8")
            if content[-5:] != "Finsh":
                self._data_buffer = self._data_buffer + content
            else:
                content = self._data_buffer + content[:-5]
                if content[0:13] == "CurrentHeight":
                    obj = SendMsg()
                    self.sendData("OK"+"|"+obj.version+"|"+obj.BestHeight+"|"+obj.Cblock)
                elif content[0:7] == "Lastest":
                    self.transport.loseConnection()
                elif content[0:5] == "False":
                    Log.Error("Synchronization failure from(Inconsistencies in\
                                version information): " + self.transport.getPeer().host)
                    self.transport.loseConnection()
                elif content[0:4] == "Text":
                    content = content[4:]
                    if dealData().storeData(content) == "restart":
                        Server.startMine()
                    self.transport.loseConnection()
                else:
                    Log.Error("BClient TSC Invalid data("+self.transport.getPeer().host+")")


class TSClntFactory(protocol.ClientFactory):
    protocol = TSClntProtocol
    clientConnectionLost = clientConnectionFailed = lambda self,connector,reason:reactor.stop()


class STSClntProtocol(protocol.Protocol):
    """
    获取对方的区块高度
    """
    _data_buffer = ""
    def sendData(self,data):
        print(data)
        if data:
            if type(data) == type("s"):
                data = data.encode("utf-8")
            self.transport.write(data+b"Finsh")
        else:
            self.transport.loseConnection()


    def connectionMade(self):
        obj = SendMsg()
        data = "Initialization"+"|"+obj.version+"|"+obj.BestHeight+"|"+obj.Cblock+"|"+obj.ipaddr
        self.sendData(data)


    def dataReceived(self,data):
        if data:
            content = data.decode("utf-8")
            if content[-5:] != "Finsh":
                self._data_buffer = self._data_buffer + content
            else:
                content = self._data_buffer + content[:-5]
                if content[0:13] == "CurrentHeight":
                    with open("bsize.atc","w",encoding="utf-8") as fp:
                        fp.write(content[14:])
                    self.transport.loseConnection()

                elif content[0:7] == "Lastest":
                    with open("bsize.atc","w",encoding="utf-8") as fo:
                        fo.write(str(Conlmdb().dbsize()))
                    self.transport.loseConnection()
                else:
                    Log.Error("BClient STSC Invalid data("+self.transport.getPeer().host+"): "+content)
                    self.transport.loseConnection()
        else:
            self.transport.loseConnection()


class STSClntFactory(protocol.ClientFactory):
    protocol = STSClntProtocol
    clientConnectionLost = clientConnectionFailed = lambda self,connector,reason:reactor.stop()


class BTSClntProtocol(protocol.Protocol):
    """
    最新区块的广播
    """
    def sendData(self,data):
        if data:
            if type(data) == type("s"):
                data = data.encode("utf-8")
            self.transport.write(data+b"Finsh")
        else:
            self.transport.loseConnection()


    def connectionMade(self):
        db = Conlmdb()
        datas = db.get(db.get("l"))+"Finsh"
        self.sendData("Getdata:" + str(db.dbsize()) + ":" + datas)
        self.transport.loseConnection()


class BTSClntFactory(protocol.ClientFactory):
    protocol = BTSClntProtocol
    clientConnectionLost = clientConnectionFailed = lambda self,connector,reason:reactor.stop()


def sendBlock():
    #广播区块
    iplist = DataProcess.getIp()
    for ip in iplist:
        HOST = ip
        PORT = Utils().sport
        reactor.connectTCP(HOST, PORT, BTSClntFactory())
        reactor.run()


def getSize():
    """
    钱包客户端获取最新区块大小
    :return:
    """
    HOST = Utils().server
    PORT = Utils().sport
    reactor.connectTCP(HOST, PORT, STSClntFactory())
    reactor.run()


def main(p=-1,ipaddr=0):
    """
    钱包客户端区块同步
    :return:
    """
    pid.put(p)
    if ipaddr == 0:
        HOST = Utils().server
    else:
        HOST = ipaddr
    PORT = Utils().sport
    reactor.connectTCP(HOST,PORT,TSClntFactory())
    reactor.run()