import Hashsum
from Utils import Utils

class POW():
    """
    工作量证明机制
    给区块设定一个有效的值，想要加入区块链的区块必须满足该值才可以
    主要的目的是对区块的挖掘制造工作量，只有当工作量被认可时才能计入有效
    block：需要判断的区块
    target：目标，也就是最低的阀值，需要满足小于这个值
    targetBits：生成目标的关键大小，比特币中使用动态调控的方法，这里暂时使用硬编码的方式
    """
    def __init__(self):
        self.targetBits = Utils().pownum
        self.target = self.gettarget()


    def getresult(self,hash):
        return True if self.target>hash else False


    def VailPow(self,block):
        """
        :param block: 区块数据
        :return: 验证工作量证明是否成功
        """
        Timestamp = block.Headers.Timestamp
        PrevBlockHash = block.Headers.PrevBlockHash
        Data = block.Headers.Meroot
        Nonce = block.Headers.Nonce
        Bits = block.Headers.Bits
        hashsum = Hashsum.Enhash(Timestamp+PrevBlockHash+str(Nonce)+Bits+Data)
        return True if self.getresult(hashsum) else False


    def gettarget(self):
        #生成有效区块的阀值
        gap = int(self.targetBits/4)
        target = "1"
        for i in range(gap-1):
            target = "0"+target
        for i in range(64-gap):
            target+="0"
        return target

