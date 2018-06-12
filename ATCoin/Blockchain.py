from Block import Block
from ProofOfWork import POW
from Conlmdb import Conlmdb
from Wallet import Wallet
from Utils import Utils
from queue import Queue
import Transaction
import MerkleTree
import Jsonstr
import PickleStr
import Log
import UTXOSet
import Crypt
import TClient
import os
import signal


class Blockchain():
    """
    区块链结构以及相关操作
    """
    ###############################################################
    #                             区块链                           #
    #                              相关                            #
    ###############################################################

    Keys = Queue()
    def __init__(self):
        #保持数据库常连接状态
        self.db = Conlmdb()


    def addblock(self):
        """
        添加区块
        data中含有
        source：来源地址
        dest：目的地址
        amount：转账数量
        """
        #添加区块
        db = Conlmdb("tranpool")
        mer = None
        tsize = db.dbsize()
        keys = []#存储正在被挖矿的交易
        if tsize >= 1:
            dtrans = db.rawiter()
            trans = []
            for key,value in dtrans.items():
                keys.append(key)
                trans.append(PickleStr.toObj(value))
                if value[:1] != b"U":
                    db.set(key, b"U"+value)
            trans.append(self.mineTran("520",Wallet().Address))
            mer = MerkleTree.Merkle(trans).getresult()
        if mer:
            block = Block(mer,self.db.get("l"))
            if POW().VailPow(block):
                self.db.put(block.Headers.gethash(), str(block))
                self.db.delete("l")
                self.db.put("l", block.Headers.gethash())
                for key in keys:
                    #删除挖矿成功的交易
                    db.delete(key)
            else:
                pass
        else:
            pass


    def updateblock(self,block,pid):
        """
        更新区块
        :param block:区块
        :param pid:挖矿进程号
        :return:
        """

        pbh = block["Headers"]["PrevBlockHash"]
        bh = block["Headers"]["Hash"]
        if self.db.get("l") == pbh:
            self.db.put(bh, block)
            self.db.delete("l")
            self.db.put("l", bh)
            if pid != -1 and not self.ConfirmT(block["Data"]["level0"],pid):
                return "restart"
            return True
        elif self.db.get(pbh):
            dlist = self.db.iter(goal=pbh)
            for bkey in dlist.keys():
                self.db.delete(bkey)
            self.db.put(bh, block)
            self.db.delete("l")
            self.db.put("l", bh)
            if pid != -1 and not self.ConfirmT(block["Data"]["level0"],pid):
                return "restart"
            return True

        elif self.db.dbsize() == 0:
            #数据库为空的情况
            self.db.put(bh,block)
            self.db.put("l",bh)
            if pid != -1 and not self.ConfirmT(block["Data"]["level0"],pid):
                return "restart"
            return True

        else:
            return False


    def ConfirmT(trans, pid):
        """
        确认交易,将有的交易从内存池中删除
        :return:True满足不需要重新启动  False不满足需要重新启动
        """
        signall = True
        once = True
        db = Conlmdb("tranpool")
        for tran in trans:
            otran = PickleStr.toObj(tran)
            goal = db.get(otran.ID)
            if goal:
                if goal[:1] == "U" and once:
                    os.kill(pid, signal.SIGKILL)
                    signall = False
                    once = False
                db.delete(otran.ID)
        return signall


    def FindTransaction(self,ID):
        """
        寻找vin中交易
        :param ID: 交易ID
        :return: 交易
        """
        bci = self.db.iter()
        for block in bci.values():
            block = Jsonstr.toJson(block)
            for i in block["Data"]["level0"]:#这里是交易信息
                tx = PickleStr.toObj(i)
                if tx.ID == ID:
                    return tx
        Log.Panic("Transaction is not found,the ID is:"+str(ID))
        return None


    def SignTransaction(self,tx,privkey):
        """
        签名交易
        :param tx: 交易
        :param privkey: 私钥
        :return:
        """
        prevTXs = dict()
        for vin in tx.Vin:
            prevTX = self.FindTransaction(vin.Txid)
            prevTXs[prevTX.ID] = prevTX
        tx.Sign(privkey,prevTXs)
        return tx


    def VerifyTransaction(self,tx):
        """
        验证交易
        :param tx: 交易
        :return:验证结果
        """
        try:
            prevTxs = dict()
            for vin in tx.Vin:
                prevTx = self.FindTransaction(vin.Txid)
                prevTxs[prevTx.ID] = prevTx
            return tx.Verify(prevTxs)
        except:
            return False


    def creatblock(self):
        """
        创建创世区块
        :param dest:自己的地址
        :return:
        """
        dest = Crypt.AtoPHK(Wallet().Address)
        tx = self.NewCoinbaseTX(dest)
        # 创世区块
        block = Block(tx.getresult())
        self.db.put(block.Headers.gethash(), str(block))
        self.db.put("l", block.Headers.gethash())
        block.getstring()


    def mineTran(self,data,dest):
        """
        创建奖励交易
        :param data: 随机内容
        :param dest: 自己的地址
        :return:
        """
        txin = Transaction.TranInput("", -1, data)
        txout = Transaction.TranOutput(Utils().subsidy, dest)
        tx = Transaction.Transaction(None, [txin], [txout])
        tx.iscoinbase = True
        tx.SetID()
        return tx


    def NewCoinbaseTX(self,dest):
        #创建基本交易
        # subsidy = 50  # 每次获得的奖励
        data = "Genesis Block Of ATCoin"
        tx = self.mineTran(data,dest)
        mer = MerkleTree.Merkle([tx])  #创世区块，里面只包含一个交易信息，也就是挖矿奖励，不包含任何的输出，典型的先有鸡操作。
        return mer


    def getMerTree(self):
        pass#生成默克尔树


    ###############################################################
    #                             交易                             #
    #                             相关                             #
    ###############################################################


    def dealTrans(self,data):
        """
        生成一个交易
        :param data: 接收方，发送数量
        :return: 生成交易是否成功
        """
        (dest, amount) = data
        trandb = Conlmdb("tranpool")
        source = Wallet().PublicKey
        fso = self.FindSpendableOutputs(source, amount)
        if fso:
            data = Transaction.Transaction().NewUTXOTransaction(source, dest, amount, fso)
            privkey = Wallet().PrivateKey
            stc = self.SignTransaction(data,privkey)
            trandb.put(stc.ID,PickleStr.toStr(stc))
            TClient.main(stc.ID)
            if TClient.end[0]:
                bd = Conlmdb("utxo")
                while not self.Keys.empty():
                    bd.delete(self.Keys.get())#更新数据库中的信息
                return True
            else:
                trandb.delete(stc.ID)#删除没有发送成功的交易，主要发生在没有网的时候，保证tranpool中没有无效的交易
        return None


    def  FindSpendableOutputs(self,public_key,amount):
        """
        unspentOutputs:没有花费的输出
        unspentTXs:没有花费的交易
        accumulated:累计个数
        """
        unspentOutputs = dict()
        u = UTXOSet.UTXOSet()
        unspentTXs = u.getUXTOs()
        accumulated = 0
        amount = int(amount)
        pubKeyHash = Crypt.getHashPubKey(public_key)
        for key,tx in unspentTXs.items():
            tx = PickleStr.toObj(tx.decode("utf-8"))
            txid = tx.ID
            unspentOutputs[txid] = []
            for outIdx in range(len(tx.Vout)):
                out = tx.Vout[outIdx]
                if out.IsLockedWithKey(pubKeyHash) and accumulated < amount:
                    accumulated += out.Value
                    unspentOutputs[txid].append(outIdx)
                    tx.Vout.pop(outIdx)
                    self.Keys.put(key)
                    if accumulated >= amount:
                        return accumulated, unspentOutputs