import ecdsa
import base58
import os
import Hashsum
import binascii
from Utils import Utils
import Log

"""
数字货币使用到的双向加密算法（非对称加密、base58加密）
1.ecdsa椭圆曲线加密
2.base58编码
"""

version = Utils().addrversion.encode("utf-8")
def b58encode(data):
    #进行base58编码
    if type(data) != type(b""):
        data = bytes(data.encode("utf-8"))
        return base58.b58encode(data)
    else:
        return base58.b58encode(data)


def b58decode(data):
    #解base58码
    return base58.b58decode(data)


def creatKeyPair():
    try:
        with open("ecdsakeys/privatekey","wb") as fo:
            private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1).to_string()
            fo.write(private_key)
    except Exception as e:
        e = "写入私钥失败："+str(e)
        Log.Error(e)


def getKeypair():
    if not os.path.isfile("ecdsakeys/privatekey"):
        creatKeyPair()
    private_key,printablepk = getPrivateKey()
    public_key,address = getPublicKey(private_key)
    public_hashkey = getHashPubKey(public_key)
    return private_key,printablepk,public_key,public_hashkey,address


def getPrivateKey():
    """
    生成私钥与可以见私钥（用户私钥）
    1.私钥用于生成公钥或者验证等
    2.可见私钥用于验证登陆等
    3.现阶段私钥的长度是32字节
    4.现阶段可见私钥的长度是60字节
    """
    try:
        with open("ecdsakeys/privatekey","rb") as fp:
            private_key = fp.read()
            checksum = Hashsum.Enhash(Hashsum.Enhash(private_key))[:4].encode("utf-8")
            pk = version + private_key + checksum
            printablepk = b58encode(pk)
            return private_key, printablepk
    except Exception as e:
        e = "读取私钥失败："+str(e)
        Log.Error(e)



def getSignInfo(signkey,message):
    """
    :param signkey: 签名的key
    :param message: 需要签名的信息
    :return: 签好名的数据
    """
    return signkey.sign(message)


def getVerifyInfo(verifykey,sig,message):
    """
    :param verifykey: 验证的key
    :param sig: 签好名的数据
    :param message: 需要签名的信息
    :return:
    """
    try:
        return ecdsa.VerifyingKey.from_string(verifykey, curve=ecdsa.SECP256k1).verify(sig,message)
    except Exception as e:
        e = "Crypt验证出错."+str(e)
        Log.Error(e)
        return False


def getPublicKey(private_key):
    """
    生成公钥
    """
    signkey = getSignKey(private_key)
    if not os.path.exists("ecdsakeys/publickey"):
        public_key = getVerifyKey(signkey)
        try:
            with open("ecdsakeys/publickey","wb") as fo:
                fo.write(public_key)
        except Exception as e:
            e = "写入公钥失败："+str(e)
            Log.Error(e)
    else:
        try:
            with open("ecdsakeys/publickey","rb") as fp:
                public_key = fp.read()
        except Exception as e:
            e = "读取公钥失败："+str(e)
            Log.Error(e)
    address = getAddress(public_key)
    return public_key,address


def getVerifyKey(signkey):
    """
    :param signkey: 签名所需要的key
    :return: 验证需要的key
    """
    verifyKey = signkey.get_verifying_key()
    public_key = verifyKey.to_string()
    return public_key


def getSignKey(private_key):
    """
    获取签名key
    """
    return ecdsa.SigningKey.from_string(private_key,curve=ecdsa.SECP256k1)


def getHashPubKey(public_key):
    """
    获取hash过的公钥
    """
    return Hashsum.Ripemd160(Hashsum.Enhash(public_key)).encode("utf-8")


def getAddress(public_key):
    """
    生成地址
    """
    hashed_key = getHashPubKey(public_key)
    tocheck_hash_key = version + hashed_key
    checksum = binascii.hexlify(Hashsum.Enhash(Hashsum.Enhash(tocheck_hash_key))[:4].encode("utf-8"))
    address = b58encode(binascii.unhexlify(tocheck_hash_key + checksum))
    return address

def AtoPHK(address):
    """
    :param address:地址
    :return: 地址转化为hashpubkey
    """
    pubKeyHash = b58decode(address)
    pubKeyHash = pubKeyHash[1:-4]
    return binascii.hexlify(pubKeyHash)
