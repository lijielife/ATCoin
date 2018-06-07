import Log
import Hashsum
import Crypt
import binascii


class Transaction():
    """
    交易信息的数据结构
    ID:交易号
    Vin:交易的输入列表
    Vout:交易的输出列表
    iscoinbase:判断是否为挖矿交易
    """


    def __init__(self,ID=None,Vin=None,Vout=None):
        self.ID = ID
        self.Vin = Vin
        self.Vout = Vout
        self.iscoinbase = False


    def NewUTXOTransaction(self,source,dest,amount,fso):
        #新建一个交易
        inputs = list()
        outputs = list()
        acc,validOutPuts = fso
        dest = Crypt.AtoPHK(dest)
        if acc < amount:
            Log.Panic("ERROR: Not enough funds!")
            return None
        else:
            #创建一个输入列表
            for txid in validOutPuts.keys():
                outs = validOutPuts[txid]
                for out in outs:
                    input = TranInput(txid,out,None,source)
                    inputs.append(input)

            #创建一个输出列表
            #只能有两个输出
            outputs.append(TranOutput(amount,dest))#转给对方
            if acc > amount:
                outputs.append(TranOutput(acc-amount,Crypt.getHashPubKey(source)))#找零
            tx = Transaction(None,inputs,outputs)
            tx.SetID()
            return tx


    def isCoinbase(self):
        return self.iscoinbase


    def SetID(self):
        #设置交易的ID
        self.ID = Hashsum.Enhash(str({"ID":self.ID,"Vin":self.Vin,"Vout":self.Vout,"iscoinbase":self.iscoinbase}))


    def Sign(self,privkey,prevTXs):
        """
        :param privkey:私钥信息
        :param prevTXs:交易字典
        描述信息：对部分信息进行签名
        """
        if self.iscoinbase:
            return
        txCopy = self.TrimmedCopy()
        for inID in range(len(txCopy.Vin)):
            vin = txCopy.Vin[inID]
            prevTX = prevTXs[vin.Txid]
            txCopy.Vin[inID].Signature = None
            txCopy.Vin[inID].PubKey = prevTX.Vout[vin.Vout].PubKeyHash
            txCopy.SetID()
            txCopy.Vin[inID].PubKey = None
            signature = Crypt.getSignInfo(Crypt.getSignKey(privkey),txCopy.ID.encode("utf-8"))
            self.Vin[inID].Signature = signature
            print(signature,txCopy.ID)


    def Verify(self,prevTXs):
        """
        :param prevTXs:交易信息
        :return: 验证结果
        """
        txCopy = self.TrimmedCopy()
        for inID in range(len(self.Vin)):
            vin = self.Vin[inID]
            prevTX = prevTXs[vin.Txid]
            txCopy.Vin[inID].Signature = None
            txCopy.Vin[inID].PubKey = prevTX.Vout[vin.Vout].PubKeyHash
            txCopy.SetID()
            txCopy.Vin[inID].PubKey = None
            if not Crypt.getVerifyInfo(vin.PubKey,vin.Signature,txCopy.ID.encode("utf-8")):
                return False
        return True


    def TrimmedCopy(self):
        """
        修剪交易
        :return:
        """
        inputs = []
        outputs = []
        for vin in self.Vin:
            inputs.append(TranInput(vin.Txid,vin.Vout,None,None))
        for vout in self.Vout:
            outputs.append(TranOutput(vout.Value,vout.PubKeyHash))
        txCopy = Transaction(self.ID,inputs,outputs)
        return txCopy


class TranOutput():
    """
    定义币的输出
    Value:一定量的币
    PubKeyHash:接收方的地址生成的公钥
    """


    def __init__(self,Value,PubKeyHash):
        self.Value = Value
        self.PubKeyHash = PubKeyHash


    def __repr__(self):
        return str({"Value":self.Value,"PubKeyHash":self.PubKeyHash})


    def CanBeUnlockedWith(self,data):
        return self.ScriptPubkey == data



    def IsLockedWithKey(self,pubKeyHash):
        return self.PubKeyHash == pubKeyHash


class TranInput():
    """
    定义币的输入
    Txid:存储的是之前交易的ID
    Vout:存储的是该输出在那笔交易中的输出索引
    Signature:交易签名
    PubKey:发送方的公钥
    """


    def __init__(self,Txid = None,Vout = None,Signature = None,PubKey = None):
        self.Txid = Txid
        self.Vout = Vout
        self.Signature = Signature
        self.PubKey = PubKey


    def __repr__(self):
        return str({"Txid":self.Txid,"Vout":self.Vout,"Signature":self.Signature,"PubKey":self.PubKey})


    def CanUnlockOutputWith(self,data):
        return self.ScriptSig == data


    def UseKey(self,pubKeyHash):
        lockingHash = Crypt.getHashPubKey(self.PubKey)
        return lockingHash == pubKeyHash

