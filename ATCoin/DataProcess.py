from ProofOfWork import POW
from Blockchain import Blockchain
import os
import Log
import Jsonstr
import Hashsum
import BClient



def addIp(ipaddr):
    """
    处理ip地址，维持一个IP表
    """
    iplist = []
    try:
        with open("ipaddr.atc","r",encoding="utf-8") as fp:
            iplist = fp.readlines()
    except Exception as e:
        Log.Error(e)
    try:
        with open("ipaddr.atc","a",encoding="utf-8") as fo:
            if ipaddr not in iplist:
                fo.write(os.linesep)
                fo.write(ipaddr)
    except Exception as e:
        Log.Error(e)

def getIp():
    """
    获取ip地址，便于传输
    :return:
    """
    try:
        with open("ipaddr.atc","r",encoding="utf-8") as fp:
            iplist = fp.readlines()
            if iplist:
                iplist.pop(0)
                return iplist
    except Exception as e:
        Log.Error(e)
    return None


def Caluhash(key,block):
    Timestamp = block["Headers"]["Timestamp"]
    PrevBlockHash = block["Headers"]["PrevBlockHash"]
    Data = block["Headers"]["Meroot"]
    Nonce = block["Headers"]["Nonce"]
    Bits = block["Headers"]["Bits"]
    hashsum = Hashsum.Enhash(Timestamp + PrevBlockHash + str(Nonce) + Bits + Data)
    return True if key==hashsum else False


def ConfirmB(data,pid):
    """
    确认区块
    data:输入的字符串
    :return:True满足 False不满足
    """
    content = data.split(":")
    key = content[0]#键，看看是否满足工作量证明
    height = content[1]
    value = content[2]#值，检查是否算出的值为key值和交易是否正常
    if POW().getresult(key):
        block = Jsonstr.toJson(value)
        if Caluhash(key,block):
            Blockchain().updateblock(block,pid)
            BClient.sendBlock()
            return True
    else:
        return False


def SyncBlock(pid):
    BClient.main(pid)
