import Hashsum
import math
import PickleStr
import Blockchain
import Log

class Merkle():
    """
    建立一个merkle树

            Hash1234
    Hash12          Hash34
  Hash1 Hash2     Hash3 Hash4
data1    data2   data3   data4
    """
    def __init__(self,trans):
        #建立一颗默克尔树
        # trans = verifyTran(trans)改为接收的时候即验证
        self.otrans = self.getPickelT(trans)
        self.trans = self.getHtrans(self.otrans)
        length = len(self.otrans)

        self.levels = list()
        self.levels.append(self.trans)

        num = math.log(length,2)
        level = int(num)

        level = level if level==num else level+1
        for i in range(level):
            self.levels.append(self.getLevel(self.levels[i]))


    def getresult(self):
        # 形成标准的输出格式
        result = dict()
        result["level0"] = self.otrans
        j = 0
        for i in self.levels:
            j += 1
            result["level" + str(j)] = i
        return result


    def getHtrans(self,trans):
        #对原始数据进行求hash处理
        result = []
        for i in trans:
            result.append(Hashsum.Enhash(i))
        return result


    def getLevel(self,tran):
        #迭代计算父节点hash
        result = []
        length = len(tran)
        if length%2 != 0:
            tran.append("")
        for i in range(0,len(tran)-1,2):
            result.append(Hashsum.Enhash(tran[i]+tran[i+1]))
        return result


    def getPickelT(self,trans):
        #序列化交易信息
        otrans = []
        for i in trans:
            otrans.append(PickleStr.toStr(i))
        return otrans


    def getroot(self):
        #输出更节点的哈希值
        return self.levels[-1][0]


def verifyTran(trans):
    """
    生成默克尔树的同时对交易的正确性进行验证
    :param trans: 原始交易列表
    :return: 剔除了
    """
    for i in range(len(trans)):
        tx = trans[i]
        if not tx.isCoinbase():
            if Blockchain.Blockchain().VerifyTransaction(tx) == False:
                Log.Panic("Error: invalid transaction,the ID is:" + tx.ID)
                trans.pop(i)
                pass  # 内存池中删除该交易
    return trans














