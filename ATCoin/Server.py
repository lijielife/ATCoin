from Utils import Utils
from Conlmdb import Conlmdb
from concurrent import futures
from Blockchain import Blockchain
from multiprocessing import Manager
from twisted.internet import protocol,reactor
import os
import Log
import Jsonstr
import BClient
import PickleStr
import MerkleTree
import DataProcess



pids = Manager().dict()
class DealData:
    """
    处理通信中的数据
    """
    def Initialization(self,init):
        contents = init.split("|")
        version = contents[1]
        BestHeight = contents[2]
        if contents[4]:#客户端参与挖矿
            DataProcess.addIp(contents[4])
        db = Conlmdb()
        if version == Utils().blockversion:
            #验证版本号是否一致
            if BestHeight >= str(db.dbsize()):
                return "Lastest"
            else:
                return str(db.dbsize())
        else:
            return None


    def getData(self,init):
        """
        :param tip:获取数据
        :return:
        """
        Cblock = init.split("|")[3]
        db = Conlmdb()
        return db.iter(goal=Cblock)



class TSServProtocol(protocol.Protocol):
    """
    区块信息交换服务器配置
    """
    _data_buffer = ""
    def senData(self,data):
        print(data)
        if data:
            if type(data) == type("s"):
                data = data.encode("utf-8")
            self.transport.write(data+b"Finsh")

    def connectionMade(self):
        """
        :客户端连接后记录到日志中去
        """
        clnt = self.clnt = self.transport.getPeer().host
        Log.Access("Block server connecting client:"+clnt)
        print("...connected from:",clnt)


    def dataReceived(self,data):
        """
        :param data:接收的区块链文本
        :接收文本--->处理文本--->发送文本
        发送给客户端最后的文本
        """
        if data:
            content = data.decode("utf-8")
            if content[-5:].strip() != "Finsh":
                self._data_buffer = self._data_buffer + content
            else:
                content = self._data_buffer + content[:-5]
                if content[0:14] == "Initialization":
                    CurrentHeight = DealData().Initialization(content)
                    if CurrentHeight == "Lastest":
                        self.senData(CurrentHeight)
                    elif CurrentHeight:
                        self.senData("CurrentHeight"+CurrentHeight)
                    else:
                        self.senData("False")

                elif content[0:2] == "OK":
                    recontent = DealData().getData(content)
                    btexts = b"Text"+Jsonstr.toStr(recontent).encode("utf-8")
                    self.senData(btexts)

                elif content[0:7] == "Getdata":
                    contents = content.split(":")
                    count = int(contents[1]) - Conlmdb().dbsize()
                    if count == 1:
                        if DataProcess.ConfirmB(contents[2],pids["Mine"]) == "restart":
                            startMine()
                    elif count >=2:
                        DataProcess.SyncBlock(pids["Mine"],ipaddr=self.clnt)
                    """
                    处理接收的信息
                    1.验证交易
                    2.去掉内存池交易
                    3.继续转发
                    """
                else:
                    Log.Error("Server TSS Invalid data("+self.clnt+")")


class TTSServProtocol(protocol.Protocol):
    """
    区块信息交换服务器配置
    """
    _data_buffer = ""
    def senData(self,data):
        if data:
            if type(data) == type("s"):
                data = data.encode("utf-8")
            self.transport.write(data + b"Finsh")

    def connectionMade(self):
        """
        :客户端连接后记录到日志中去
        """
        clnt = self.clnt = self.transport.getPeer().host
        Log.Access("Trans server Connecting client:"+clnt)
        print("...connected from:",clnt)


    def dataReceived(self,data):
        """
        :param
        data: 接收交易的的文本
        :接收文本 - -->处理文本 - -->发送文本
        发送给客户端最后的文本
        """
        if data:
            content = data.decode("utf-8")
            if content[-5:] != "Finsh":
                self._data_buffer = self._data_buffer + content
            else:
                content = self._data_buffer + content[:-5]

                if content[0:14] == "Initialization":
                    if content.split("|")[1] == Utils().addrversion:
                        self.senData("OK")
                    else:
                        self.senData("False")

                elif content[0:4] == "Tran":
                    stc = PickleStr.toObj((content[4:]))
                    trans = MerkleTree.verifyTran([stc])#对交易进行验证，防止错误交易蔓延
                    if trans:
                        db = Conlmdb("tranpool")
                        for tran in trans:
                            db.put(tran.ID,tran)
                        self.senData("GetTran")
                    else:
                        self.senData("ErrorTran")
                else:
                    Log.Error("Server TTSS Invalid data(" + self.clnt + "): ")


def Bcom():
    """
    区块进程
    :return:
    """
    pids["Bcom"] = os.getpid()
    PORT = Utils().sport
    factory = protocol.Factory()
    factory.protocol = TSServProtocol
    print("Waiting for blocks transmission...")
    reactor.listenTCP(PORT, factory)
    reactor.run()


def Tcom():
    """
    交易通信
    :return:
    """
    pids["Tcom"] = os.getpid()
    PORT = Utils().tport
    factory = protocol.Factory()
    factory.protocol = TTSServProtocol
    print("Waiting for trans transmission...")
    reactor.listenTCP(PORT, factory)
    reactor.run()


def Mine():
    """
    挖矿进程
    :return:
    """
    pids["Mine"] = os.getpid()
    while True:
        Blockchain.addblock()
        os.sleep(6)


def startMine():
    """
    重启挖矿进程
    :return:
    """
    with futures.ProcessPoolExecutor(max_workers=2) as executor:
        executor.submit(Mine)


if __name__ == "__main__":
    with futures.ProcessPoolExecutor(max_workers=4) as executor:
        executor.submit(Bcom)
        executor.submit(Tcom)
        executor.submit(Mine)
        if Conlmdb().dbsize()==0:
            executor.submit(BClient.main)



