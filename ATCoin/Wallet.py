import Crypt

class Wallet:
    """
    钱包类
    """
    def  __init__(self):
        PrivateKey,PrintPubey,PublicKey,PublicHashKey,Address = Crypt.getKeypair()
        self.PrivateKey = PrivateKey
        self.PrintPubkey = PrintPubey
        self.PublicKey = PublicKey
        self.PublicHashKey = PublicHashKey
        self.Address = Address



class Wallets:
    """
    钱包集合
    """
    def __init__(self):
        self.wallets = []





