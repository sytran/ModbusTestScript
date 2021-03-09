"""
    Class for creating a Modbus tree structure (subclass of wx.TreeCtrl)
"""

__version__ = "$Revision: 1.0.0 $"
__author__ = "Wayne Smith"
__status__ = "Internal"
__date__ = "01 February 2021"

from DeviceFrame import *
from ModbusTreeNodes import *


class ModbusTree(wx.TreeCtrl):
    detailsType = 0
    addressType = 0
    devicesType = 1
    detailsNode = 0
    devicesNode = 1
    singleDeviceIdType = "i"
    deviceIndex = None
    devices = None
    currentDevice = None
    networkData = None
    nodeDictionary = {}
    root = None
    networkRoot = None
    _parent = None
    details = Details

    def intitalizeTree(self, datasource=None):
        if datasource is None:
            self.networkData = self.generateMockData(4)
        else:
            self.networkData = datasource

        self.root = self.AddRoot("Network Tree")
        self.SetItemData(self.root, ('key', 'value'))

        for network in self.networkData:
            self.networkRoot = self.AppendItem(self.root, "Network")
            self.SetItemHasChildren(self.networkRoot)
            self.SetItemData(self.networkRoot, network.nodeFamily)

        self.Expand(self.root)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.onItemExpanding)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSING, self.onItemCollapsing)

    def collapseAllAndUpdate(self, datasource):
        for key in self.nodeDictionary.keys():
            del self.nodeDictionary[key]
        self.CollapseAllChildren(self.networkRoot)
        self.networkData = datasource

    def __init__(self, parent, id, pos, size, style):
        self._parent = parent
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style)

    def generateMockData(self, numberOfNetworks):
        networks = []
        for j in range(numberOfNetworks):
            devices = []
            detailsNode = Details([j, 0], 23, 1600, 1, 1, 1, 1)
            for i in range(2):
                deviceName = "Device " + str(i + 1)
                liveDataNode = LiveData([j, 1, i, 0], 1.23, 1.24)
                deviceNode = Device([j, 1, i], deviceName, i + 1, liveDataNode)
                devices.append(deviceNode)
            devicesNode = Devices([j, 1], devices)
            networkName = "Network " + str(j + 1)
            networks.append(Network([j], networkName, "Online", detailsNode, devicesNode))
        return networks

    def nodeFamilyToNodeKey(self, nodeFamily):
        nodeKey = ""
        for i in nodeFamily:
            nodeKey += str(i)
        return nodeKey

    def onItemExpanding(self, event):
        item = event.GetItem()
        nodeFamily = self.GetItemData(item)
        self.nodeDictionary[self.nodeFamilyToNodeKey(nodeFamily)] = item
        self.updateNodeForNodeFamily(nodeFamily, item)

    def onItemCollapsing(self, event):
        if self.nodeDictionary:
            item = event.GetItem()
            nodeFamily = self.GetItemData(item)
            del self.nodeDictionary[self.nodeFamilyToNodeKey(nodeFamily)]

    def updateNodeFamily(self, networkIndex, deviceIndex, type, nodeFamily, newValue):
        nodeKey = self.nodeFamilyToNodeKey(nodeFamily)
        if nodeKey in self.nodeDictionary:
            nodeForKey = self.nodeDictionary[nodeKey]
            # update network
            if type == "COND_RES1":
                self.networkData[networkIndex].devices.devices[deviceIndex].livedata.COND_RES1 = newValue
            elif type == "COND_RES1_TEMP":
                self.networkData[networkIndex].devices.devices[deviceIndex].livedata.COND_RES1_TEMP = newValue
            elif type == "COND_RES2":
                self.networkData[networkIndex].devices.devices[deviceIndex].livedata.COND_RES2 = newValue
            elif type == "COND_RES2_TEMP":
                self.networkData[networkIndex].devices.devices[deviceIndex].livedata.COND_RES2_TEMP = newValue
            elif type == "PH_ORP":
                self.networkData[networkIndex].devices.devices[deviceIndex].livedata.PH_ORP = newValue
            elif type == "PH_ORP_TEMP":
                self.networkData[networkIndex].devices.devices[deviceIndex].livedata.PH_ORP_TEMP = newValue
            self.updateNodeForNodeFamily(nodeFamily, nodeForKey)

    def updateNodeForNodeFamily(self, nodeFamily, item):
        networkIndex = 0
        elementCount = len(nodeFamily)
        for i in range(elementCount):
            elementIndex = nodeFamily[i]
            level = i + 1

            if level == 1:
                # networks
                networkIndex = elementIndex
                if level == elementCount:
                    self.DeleteChildren(item)
                    thisNetwork = self.networkData[networkIndex]
                    # status
                    self.AppendItem(item, "name : " + thisNetwork.name)
                    # status
                    self.AppendItem(item, "status : " + thisNetwork.status)
                    # details
                    details = self.AppendItem(item, "details:")
                    self.SetItemHasChildren(details)
                    self.SetItemData(details, thisNetwork.details.nodeFamily)
                    # devices
                    devices = self.AppendItem(item, "devices:")
                    self.SetItemHasChildren(devices)
                    self.SetItemData(devices, thisNetwork.devices.nodeFamily)

            elif level == 2:
                # details or devices
                if level == elementCount:
                    self.DeleteChildren(item)
                    network = self.networkData[networkIndex]
                    if elementIndex == self.detailsType:
                        self._parent.showDetails()
                        # port
                        port = "Port: " + str(network.details.port)
                        self.AppendItem(item, port)
                        # buadrate
                        baudrate = "Baudrate: " + str(network.details.baud)
                        self.AppendItem(item, baudrate)
                        # bytesize
                        bytesize = "Bitesize: " + str(network.details.bytesize)
                        self.AppendItem(item, bytesize)
                        # parity
                        parity = "Parity: " + str(network.details.parity)
                        self.AppendItem(item, parity)
                        # stopbits
                        stopbits = "Stopbits: " + str(network.details.stopbits)
                        self.AppendItem(item, stopbits)
                        # timeout
                        timeout = "Timeout: " + str(network.details.timeout)
                        self.AppendItem(item, timeout)
                    elif elementIndex == self.devicesType:
                        for device in network.devices.devices:
                            thisDevice = self.AppendItem(item, str(device.name))
                            self.SetItemHasChildren(thisDevice)
                            self.SetItemData(thisDevice, device.nodeFamily)

            elif level == 3:
                # devices
                self.currentDevice = self.networkData[networkIndex].devices.devices[elementIndex]
                if level == elementCount:
                    self.DeleteChildren(item)
                    # address
                    address = "address: " + str(self.currentDevice.address)
                    self.AppendItem(item, address)
                    # live data
                    liveData = self.AppendItem(item, "Live Data")
                    self.SetItemHasChildren(liveData)
                    self.SetItemData(liveData, self.currentDevice.livedata.nodeFamily)

            elif level == 4:
                # live data
                self.DeleteChildren(item)
                self._parent.showData(self.currentDevice.livedata, self.currentDevice.name)
                self.AppendItem(item, "COND_RES1: " + str(self.currentDevice.livedata.COND_RES1))
                self.AppendItem(item, "COND_RES1_TEMP: " + str(self.currentDevice.livedata.COND_RES1_TEMP))
                self.AppendItem(item, "COND_RES2: " + str(self.currentDevice.livedata.COND_RES2))
                self.AppendItem(item, "COND_RES2_TEMP: " + str(self.currentDevice.livedata.COND_RES2_TEMP))
                self.AppendItem(item, "PH_ORP: " + str(self.currentDevice.livedata.PH_ORP))
                self.AppendItem(item, "PH_ORP_TEMP: " + str(self.currentDevice.livedata.PH_ORP_TEMP))
