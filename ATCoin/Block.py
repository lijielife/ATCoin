import Hashsum
import time
from ProofOfWork import POW
import Jsonstr
from Utils import Utils

class Block():
    """
    区块：真正储存有效信息的结构
    Blocksize:区块体的大小，区块头的大小相对固定，暂时不考虑计算，如果需要后续在加上
    Transactioncounter:当前区块记录的交易数量
    Data:区块存储的实际有效信息，也就是交易
    Magicno:区分区块的魔术字符,现在考虑需要把这个变量放在最后面，然后才能准确的识别区块的结束位置

    """
    def __init__(self,Data,PrevBlokHash="None"):
        json = Jsonstr.toJson(Data)
        string = "level" + str(len(json) - 1)
        #区块体
        self.Data = Data
        self.Magicno = "\xd9\xb4\xbe\xf9"
        self.Transactioncounter = str(len(json["level0"]))
        self.Blocksize = str(len(self.Magicno))+str(len(Data))+self.Transactioncounter
        # 区块头
        root = str(json[string])
        self.Headers = BlockHeader(root,PrevBlokHash)


    def __repr__(self):
        return str({"Headers":{"PrevBlockHash":self.Headers.PrevBlockHash,"Hash":self.Headers.Hash,"Timestamp":self.Headers.Timestamp,
                            "Version":self.Headers.Version,"Nonce":self.Headers.Nonce,"Bits":self.Headers.Bits},
                "Blocksize":self.Blocksize,"Transactioncounter":self.Transactioncounter,
                "Data":self.Data,"Magicno":self.Magicno
                })


    def getstring(self):
        print(self.Headers.PrevBlockHash)
        print(self.Data)
        print(self.Headers.Hash)



class BlockHeader():
    """
    区块头信息
    PrevBlockHash:前一个块的哈希，即父哈希
    Hash:当前块的哈希
    Timestamp:当前时间戳，也就是区块创建的时间
    Version:版本信息
    Nonce:计数器
    Bits:难度值

    """
    def __init__(self,Meroot,PrevBlockHash):
        pow = POW()
        self.Meroot = Meroot
        self.Timestamp = str(time.time())
        self.PrevBlockHash = str(PrevBlockHash)
        self.Nonce = 0
        self.Bits = str(pow.targetBits)
        while True:
            self.Hash = Hashsum.Enhash(self.Timestamp+self.PrevBlockHash+str(self.Nonce)+self.Bits+self.Meroot)
            if pow.getresult(self.Hash):
                break
            else:
                self.Nonce +=1
        self.Version = Utils().blockversion


    def gethash(self):
        return self.Hash
