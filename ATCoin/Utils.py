import re
import Log

class Utils:
    """
    获取各个文件中配置信息
    1.配置文件中信息获取
    """
    def __init__(self):
        try:
            with open("config","r",encoding="utf-8") as fp:
                infos = fp.readlines()
            for info in infos:
                if re.match("addrversion",info):
                    self.addrversion = info.split("=")[1].strip()
                if re.match("blockversion",info):
                    self.blockversion = info.split("=")[1].strip()
                if re.match("sport",info):
                    self.sport = int(info.split("=")[1].strip())
                if re.match("server",info):
                    self.server = info.split("=")[1].strip()
                if re.match("tport", info):
                    self.tport = int(info.split("=")[1].strip())
                if re.match("miner",info):
                    self.miner = int(info.split("=")[1].strip())
                if re.match("subsidy",info):
                    self.subsidy = int(info.split("=")[1].strip())
                if re.match("pownum",info):
                    self.pownum = int(info.split("=")[1].strip())
        except Exception as e:
            print(e)
            Log.Error(e)
