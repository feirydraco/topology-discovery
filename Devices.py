import enum

class DevType(enum.Enum):
    ROUTER = 1
    SWITCH = 2
    APPLIANCE = 3


class Device:
    def __init__(self, ip, mac, did, label, dtype="Undefined"):
        self.ip = ip
        self.mac = mac
        self.did = did
        self.label = label
        self.dtype = dtype

    def getName(self):
        return self.did

    def __str__(self):
        return self.label

class NetDevice:
    def __init__(self, ip, pm, did, label, dtype="Undefined"):
        self.ip = ip
        self.pm = pm
        self.did = did
        self.dtype = dtype
        self.label = label
        self.AFT = dict()

    def getAFT(self):
        pass

    def getName(self):
        return self.dtype

    def dispAFT(self):
        for key in self.AFT:
            print(key, self.AFT[key])
    
    def __str__(self):
        return self.label