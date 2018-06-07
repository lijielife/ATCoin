from Conlmdb import Conlmdb
from Wallet import Wallet
import Jsonstr
import PickleStr

class UTXOSet():
    """
    生成为使用的输出的数据库
    针对本用户，一旦生成交易就删除这个信息
    """
    def __init__(self):
        db = Conlmdb()
        self.db = Conlmdb("utxo")
        pubKeyHash = Wallet().PublicHashKey
        startip = self.db.get("l")
        if startip:
            self.db.delete("l")
            utxos = self.FindUTXOs(pubKeyHash,db,startip)
            for key,value in utxos.items():
                self.db.put(key,value)
            self.db.put("l",self.tip)
        else:
            utxos = self.FindUTXOs(pubKeyHash,db)
            for key, value in utxos.items():
                self.db.put(key, value)
            self.db.put("l", self.tip)


    def getUXTOs(self):
        uxtos = {}
        for key,uxto in self.db.rawiter().items():
            uxtos[key] = uxto
        return uxtos


    def FindUTXOs(self,pubKeyHash,db,key="l"):
        #寻找没有花费的交易
        unspentTXs = dict()
        # spentTXOs = dict()
        bci = db.iter(tip=key)
        self.tip = db.get("l")

        def rgoto(tx):
            #实现特殊跳转功能
            for outIdx in range(len(tx.Vout)):
                Vout = tx.Vout
                txID = tx.ID
                out = Vout[outIdx]
                # if txID in spentTXOs.keys():
                #     for spentOut in spentTXOs[txID]:
                #         if spentOut == outIdx:
                #             return
                if out.IsLockedWithKey(pubKeyHash):
                    unspentTXs[txID] = PickleStr.toStr(tx)

            # if tx.isCoinbase() == False:
            #     for vin in tx.Vin:
            #         if vin.UseKey(pubKeyHash):
            #             inTxID = vin.Txid
            #             if spentTXOs.get(inTxID) == None:
            #                 spentTXOs[inTxID] = []
            #             spentTXOs[inTxID].append(vin.Vout)


        for block in bci.values():
            block = Jsonstr.toJson(block)
            for i in Jsonstr.toJson(block["Data"])["level0"]:#这里是交易信息
                tx = PickleStr.toObj(i)
                rgoto(tx)
            # if len(block["Headers"]["PrevBlockHash"]) == 0:
            #     break
        return unspentTXs
