"""
    Modbus tree node classes
"""

__version__ = "$Revision: 1.0.0 $"
__author__ = "Wayne Smith"
__status__ = "Internal"
__date__ = "10 February 2021"


class Node(object):
    def __init__(self, nodeFamily):
        self.nodeFamily = nodeFamily


class Network(Node):
    def __init__(self, nodeFamily, name, status, details, devices):
        super(Network, self).__init__(nodeFamily)
        self.name = name
        self.status = status
        self.details = details
        self.devices = devices


class Details(Node):
    def __init__(self, nodeFamily, port, baud, bytesize, parity, stopbits, timeout):
        super(Details, self).__init__(nodeFamily)
        self.port = port
        self.baud = baud
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout


class Device(Node):
    def __init__(self, nodeFamily, name, address, livedata):
        super(Device, self).__init__(nodeFamily)
        self.name = name
        self.address = address
        self.livedata = livedata


class Devices(Node):
    def __init__(self, nodeFamily, devices):
        super(Devices, self).__init__(nodeFamily)
        self.devices = devices


class LiveData(Node):
    def __init__(self, nodeFamily, COND_RES1=None, COND_RES1_TEMP=None, COND_RES2=None, COND_RES2_TEMP=None,
                 PH_ORP=None, PH_ORP_TEMP=None):
        super(LiveData, self).__init__(nodeFamily)
        self.COND_RES1 = COND_RES1
        self.COND_RES1_TEMP = COND_RES1_TEMP
        self.COND_RES2 = COND_RES2
        self.COND_RES2_TEMP = COND_RES2_TEMP
        self.PH_ORP = PH_ORP
        self.PH_ORP_TEMP = PH_ORP_TEMP
