from twisted.internet import protocol,reactor
from Utils import Utils
from Conlmdb import Conlmdb
from queue import Queue
import Log

ids = Queue()
end = [False]
tranId = Queue()

class dealData:
    """
    处理数据
    """
    db = Conlmdb("tranpool")
    def sendData(self):
        ID = ids.get()
        data = self.db.get(ID)
        if data:
            tranId.put(ID)
        return data

    def delTrans(self):
        while not tranId.empty():
            self.db.delete(tranId.get())



class TSClntProtocol(protocol.Protocol):
    """
    交易的传输
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
        data = "Initialization"+"|"+Utils().addrversion
        self.sendData(data)


    def dataReceived(self,data):
        if data:
            content = data.decode("utf-8")
            if content[-5:] != "Finsh":
                self._data_buffer = self._data_buffer + content
            else:
                content = self._data_buffer + content[:-5]
                if content[0:2] == "OK":
                    self.sendData("Tran"+dealData().sendData())
                elif content[0:5] == "False":
                    Log.Error("Synchronization failure from(Inconsistencies in\
                    version information): "+self.transport.getPeer().host)
                elif content[0:7] == "GetTran":
                    print("Server checkout transaction success")
                    dealData().delTrans()
                    end[0] = True
                    self.transport.loseConnection()
                elif content[0:9] == "ErrorTran":
                    print("Server checkout transaction error")
                    dealData().delTrans()
                    self.transport.loseConnection()
                else:
                    Log.Error("Invalid data(" + self.transport.getPeer().host + ")")




class TSClntFactory(protocol.ClientFactory):
    protocol = TSClntProtocol
    clientConnectionLost = clientConnectionFailed = lambda self,connector,reason:reactor.stop()


def main(ID):
    ids.put(ID)
    HOST = Utils().server
    PORT = Utils().tport
    reactor.connectTCP(HOST,PORT,TSClntFactory())
    reactor.run()
    
    
def rmain(ID):
    """
    :param ID:交易ID
    :return: 是否成功发送
    """
    main(ID)
    return end[0]
