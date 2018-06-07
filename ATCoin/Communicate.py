from Utils import Utils
import Log
from Conlmdb import Conlmdb
import socket
import uuid


class SendMsg:
    """
    需要发送的消息
    """
    def __init__(self):
        db = Conlmdb()
        self.version = Utils().blockversion
        self.BestHeight = str(db.dbsize())
        self.Cblock = db.get("l")
        if not self.Cblock:
            self.Cblock = "None"
        if Utils().miner:
            self.ipaddr = SetConf().ipaddr
        else:
            self.ipaddr = ""


class SetConf:
    """
    设置获取通信配置
    """
    def __init__(self):
        self.name = self.getName()
        self.ipaddr = self.getIp()
        self.macaddr = self.getMacaddr()


    def getName(self):
        """
        :return: 获取本机电脑名
        """
        return socket.getfqdn(socket.gethostname())


    def getIp(self):
        """
        :return: 获取本机ip
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 53))
            ip = s.getsockname()[0]
        except:
            ip = socket.gethostbyname_ex(socket.gethostname())[-1][-1]
            Log.Error("网络不可达！")
        finally:
            s.close()
        return ip


    def getMacaddr(self):
        """
        获取mac地址
        """
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])
