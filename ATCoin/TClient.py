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
    def sendData(self,data):
        if data:
            print("...sending "+data+"...")
            self.transport.write(data.encode("utf-8"))
        else:
            self.transport.loseConnection()


    def connectionMade(self):
        data = "Initialization"+"|"+Utils().addrversion
        self.sendData(data)


    def dataReceived(self,data):
        if data:
            content = data.decode("utf-8")
            if content[0:2] == "OK":
                self.sendData("Tran"+dealData().sendData())
                self.transport.loseConnection()
            elif content[0:5] == "False":
                Log.Error("Synchronization failure from(Inconsistencies in\
                version information): "+self.transport.getPeer().host)
            elif content[0:7] == "GetTran":
                dealData().delTrans()
                end[0] = True
                self.transport.loseConnection()
            else:
                print("Invalid data(" + self.transport.getPeer().host + "): " + data)
                Log.Error("Invalid data(" + self.transport.getPeer().host + "): " + data)




class TSClntFactory(protocol.ClientFactory):
    protocol = TSClntProtocol
    clientConnectionLost = clientConnectionFailed = lambda self,connector,reason:reactor.stop()


def main(ID):
    ids.put(ID)
    HOST = Utils().server
    PORT = Utils().tport
    reactor.connectTCP(HOST,PORT,TSClntFactory())
    reactor.run()
