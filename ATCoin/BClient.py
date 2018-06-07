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
        dbmap = Jsonstr.toJson(data[4:])
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

        return result



class TSClntProtocol(protocol.Protocol):
    def sendData(self,data):
        if data:
            print("...sending "+data+"...")
            self.transport.write(data.encode("utf-8"))
        else:
            self.transport.loseConnection()


    def connectionMade(self):
        obj = SendMsg()
        data = "Initialization"+"|"+obj.version+"|"+obj.BestHeight+"|"+obj.Cblock+"|"+obj.ipaddr
        self.sendData(data)


    def dataReceived(self,data):
        if data:
            content = data.decode("utf-8")
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
                if dealData().storeData(content) == "restart":
                    Server.startMine()
                self.transport.loseConnection()
            else:
                print("BClient TSC Invalid data("+self.transport.getPeer().host+"): "+content)
                Log.Error("BClient TSC Invalid data("+self.transport.getPeer().host+"): "+content)
                self.transport.loseConnection()



class TSClntFactory(protocol.ClientFactory):
    protocol = TSClntProtocol
    clientConnectionLost = clientConnectionFailed = lambda self,connector,reason:reactor.stop()


class STSClntProtocol(protocol.Protocol):
    def sendData(self,data):
        if data:
            self.transport.write(data.encode("utf-8"))
        else:
            self.transport.loseConnection()


    def connectionMade(self):
        obj = SendMsg()
        data = "Initialization"+"|"+obj.version+"|"+obj.BestHeight+"|"+obj.Cblock+"|"+obj.ipaddr
        self.sendData(data)


    def dataReceived(self,data):
        if data:
            content = data.decode("utf-8")
            if content[0:13] == "CurrentHeight":
                with open("bsize.atc","w",encoding="utf-8") as fp:
                    fp.write(content[content[14:]])
                self.transport.loseConnection()
                sys.exit()

            else:
                with open("bsize.atc","w",encoding="utf-8") as fo:
                    fo.write(str(Conlmdb().dbsize()))
                Log.Error("BClient STSC Invalid data("+self.transport.getPeer().host+"): "+content)
                self.transport.loseConnection()
        else:
            self.transport.loseConnection()


class STSClntFactory(protocol.ClientFactory):
    protocol = STSClntProtocol
    clientConnectionLost = clientConnectionFailed = lambda self,connector,reason:reactor.stop()


class BTSClntProtocol(protocol.Protocol):
    def sendData(self,data):
        if data:
            self.transport.write(data.encode("utf-8"))
        else:
            self.transport.loseConnection()


    def connectionMade(self):
        db = Conlmdb()
        data = db.get(db.get("l"))
        self.sendData("Getdata:"+str(db.dbsize())+":"+data)
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


def main(p=-1):
    """
    钱包客户端区块同步
    :return:
    """
    pid.put(p)
    HOST = Utils().server
    PORT = Utils().sport
    reactor.connectTCP(HOST,PORT,TSClntFactory())
    reactor.run()