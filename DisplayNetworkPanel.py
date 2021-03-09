"""
    Panel for displaying networks
"""

__version__ = "$Revision: 1.0.0 $"
__author__ = "Wayne Smith"
__status__ = "Internal"
__date__ = "09 December 2021"

from ModbusTree import *


class DeviceResponder:
    network = None
    devicePosition = None
    _parent = None
    deviceId = None

    def __init__(self, network, id, parent, position):
        self.devicePosition = position
        self.network = network
        self.deviceId = id
        self._parent = parent
        messageRefreshView = "refreshView" + str(self.network.id) + str(position)
        Publisher.subscribe(self.refreshView, messageRefreshView)

    def refreshView(self):
        self._parent.refreshView(self.deviceId, self.devicePosition - 1)


class DisplayNetworkPanel(wx.Panel):
    networkDevices = []
    network = None
    tree = None
    readingValues = False
    PORT = None
    deviceResponders = []
    isNetworkLive = False
    liveData = {}
    detailsNode = 0
    devicesNode = 1
    liveDataNode = 0
    networkNode = 0

    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)
        self.SetBackgroundColour('#000237')
        self.vboxOuter = wx.BoxSizer(wx.HORIZONTAL)
        vboxTitle = wx.BoxSizer(wx.VERTICAL)
        vboxDetail = wx.BoxSizer(wx.VERTICAL)
        self._parent = parent

        self.detailPan = wx.Panel(self)
        self.detailPan.SetBackgroundColour('#0512D2')

        # put some text with a larger bold font on it
        title = wx.StaticText(self.detailPan, label="Network Detail")
        font = title.GetFont()
        font.PointSize += 10
        font = font.Bold()
        title.SetFont(font)
        title.SetForegroundColour('#FFFFFF')
        vboxTitle.Add(title, 1, wx.ALIGN_CENTER)

        self.displayBox = wx.BoxSizer(wx.VERTICAL)
        # network detail sizer box
        networkDetailBox = wx.StaticBox(self.detailPan, -1, 'Network Detail')
        networkDetailBox.SetForegroundColour('#FFFFFF')
        self.networkDetailBoxSizer = wx.StaticBoxSizer(networkDetailBox, wx.VERTICAL)

        self.detailBox = wx.BoxSizer(wx.VERTICAL)
        self.nameLabel = wx.StaticText(self.detailPan, -1, "Name: ")
        nameFont = self.nameLabel.GetFont()
        nameFont.PointSize += 2
        nameFont = nameFont.Bold()
        self.nameLabel.SetFont(nameFont)
        self.nameLabel.SetForegroundColour('#FFFFFF')
        self.detailBox.Add(self.nameLabel, 1, wx.ALL | wx.LEFT, 5)

        self.portLabel = wx.StaticText(self.detailPan, -1, "Port: ")
        portFont = self.portLabel.GetFont()
        portFont.PointSize += 2
        portFont = portFont.Bold()
        self.portLabel.SetFont(portFont)
        self.portLabel.SetForegroundColour('#FFFFFF')
        self.detailBox.Add(self.portLabel, 1, wx.ALL | wx.LEFT, 5)

        self.baudrateLabel = wx.StaticText(self.detailPan, -1, "Baudrate:")
        baudrateFont = self.baudrateLabel.GetFont()
        baudrateFont.PointSize += 2
        baudrateFont = baudrateFont.Bold()
        self.baudrateLabel.SetFont(baudrateFont)
        self.baudrateLabel.SetForegroundColour('#FFFFFF')
        self.detailBox.Add(self.baudrateLabel, 1, wx.ALL | wx.LEFT, 5)

        self.bytesizeLabel = wx.StaticText(self.detailPan, -1, "Bytesize: ")
        bytesizeFont = self.bytesizeLabel.GetFont()
        bytesizeFont.PointSize += 2
        bytesizeFont = bytesizeFont.Bold()
        self.bytesizeLabel.SetFont(bytesizeFont)
        self.bytesizeLabel.SetForegroundColour('#FFFFFF')
        self.detailBox.Add(self.bytesizeLabel, 1, wx.ALL | wx.LEFT, 5)

        self.parityLabel = wx.StaticText(self.detailPan, -1, "Parity: ")
        parityFont = self.parityLabel.GetFont()
        parityFont.PointSize += 2
        parityFont = bytesizeFont.Bold()
        self.parityLabel.SetFont(parityFont)
        self.parityLabel.SetForegroundColour('#FFFFFF')
        self.detailBox.Add(self.parityLabel, 1, wx.ALL | wx.LEFT, 5)

        self.stopbitsLabel = wx.StaticText(self.detailPan, -1, "Stopbits: ")
        stopbitsFont = self.stopbitsLabel.GetFont()
        stopbitsFont.PointSize += 2
        stopbitsFont = stopbitsFont.Bold()
        self.stopbitsLabel.SetFont(stopbitsFont)
        self.stopbitsLabel.SetForegroundColour('#FFFFFF')
        self.detailBox.Add(self.stopbitsLabel, 1, wx.ALL | wx.LEFT, 5)

        self.timeoutLabel = wx.StaticText(self.detailPan, -1, "Timeout: ")
        timeoutFont = self.timeoutLabel.GetFont()
        timeoutFont.PointSize += 2
        timeoutFont = timeoutFont.Bold()
        self.timeoutLabel.SetFont(timeoutFont)
        self.timeoutLabel.SetForegroundColour('#FFFFFF')
        self.detailBox.Add(self.timeoutLabel, 1, wx.ALL | wx.LEFT, 5)
        self.networkDetailBoxSizer.Add(self.detailBox, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)

        # live data sizer box
        networkDataBox = wx.StaticBox(self.detailPan, -1, 'Live Data')
        networkDataBox.SetForegroundColour('#FFFFFF')
        self.networkDataBoxSizer = wx.StaticBoxSizer(networkDataBox, wx.VERTICAL)

        self.liveDataBox = wx.BoxSizer(wx.VERTICAL)
        self.deviceNameLabel = wx.StaticText(self.detailPan, -1, "Device: ")
        deviceNameFont = self.deviceNameLabel.GetFont()
        deviceNameFont.PointSize += 2
        deviceNameFont = deviceNameFont.Bold()
        self.deviceNameLabel.SetFont(deviceNameFont)
        self.deviceNameLabel.SetForegroundColour('#FFFFFF')
        self.liveDataBox.Add(self.deviceNameLabel, 1, wx.ALL | wx.LEFT, 5)

        self.condRes1Label = wx.StaticText(self.detailPan, -1, "Cond/Res1: ")
        condRes1Font = self.condRes1Label.GetFont()
        condRes1Font.PointSize += 2
        condRes1Font = condRes1Font.Bold()
        self.condRes1Label.SetFont(condRes1Font)
        self.condRes1Label.SetForegroundColour('#FFFFFF')
        self.liveDataBox.Add(self.condRes1Label, 1, wx.ALL | wx.LEFT, 5)

        self.condRes1TempLabel = wx.StaticText(self.detailPan, -1, "Cond/Res1 Temp: ")
        condRes1TempFont = self.condRes1TempLabel.GetFont()
        condRes1TempFont.PointSize += 2
        condRes1TempFont = condRes1TempFont.Bold()
        self.condRes1TempLabel.SetFont(condRes1TempFont)
        self.condRes1TempLabel.SetForegroundColour('#FFFFFF')
        self.liveDataBox.Add(self.condRes1TempLabel, 1, wx.ALL | wx.LEFT, 5)

        self.condRes2Label = wx.StaticText(self.detailPan, -1, "Cond/Res2: ")
        condRes2Font = self.condRes2Label.GetFont()
        condRes2Font.PointSize += 2
        condRes2Font = condRes2Font.Bold()
        self.condRes2Label.SetFont(condRes2Font)
        self.condRes2Label.SetForegroundColour('#FFFFFF')
        self.liveDataBox.Add(self.condRes2Label, 1, wx.ALL | wx.LEFT, 5)

        self.condRes2TempLabel = wx.StaticText(self.detailPan, -1, "Cond/Res2 Temp: ")
        condRes2TempFont = self.condRes2TempLabel.GetFont()
        condRes2TempFont.PointSize += 2
        condRes2TempFont = condRes2TempFont.Bold()
        self.condRes2TempLabel.SetFont(condRes2TempFont)
        self.condRes2TempLabel.SetForegroundColour('#FFFFFF')
        self.liveDataBox.Add(self.condRes2TempLabel, 1, wx.ALL | wx.LEFT, 5)

        self.phORPLabel = wx.StaticText(self.detailPan, -1, "pH/ORP: ")
        phORPFont = self.phORPLabel.GetFont()
        phORPFont.PointSize += 2
        phORPFont = phORPFont.Bold()
        self.phORPLabel.SetFont(phORPFont)
        self.phORPLabel.SetForegroundColour('#FFFFFF')
        self.liveDataBox.Add(self.phORPLabel, 1, wx.ALL | wx.LEFT, 5)

        self.phORPTempLabel = wx.StaticText(self.detailPan, -1, "pH/ORP Temp: ")
        phORPTempFont = self.phORPTempLabel.GetFont()
        phORPTempFont.PointSize += 2
        phORPTempFont = phORPTempFont.Bold()
        self.phORPTempLabel.SetFont(phORPTempFont)
        self.phORPTempLabel.SetForegroundColour('#FFFFFF')
        self.liveDataBox.Add(self.phORPTempLabel, 1, wx.ALL | wx.LEFT, 5)

        self.displayCellData = wx.Button(self.detailPan, -1, "Display Live Spreadsheet")
        self.displayCellData.Bind(wx.EVT_BUTTON, self.OnDisplayCellData)
        self.liveDataBox.Add(self.displayCellData, 0, wx.ALL | wx.CENTER, 20)
        self.networkDataBoxSizer.Add(self.liveDataBox, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)

        self.displayBox.Add(self.networkDetailBoxSizer, 1, wx.EXPAND | wx.ALL)
        self.displayBox.Add(self.networkDataBoxSizer, 1, wx.EXPAND | wx.ALL)
        self.displayBox.Hide(self.networkDetailBoxSizer)
        self.displayBox.Hide(self.networkDataBoxSizer)

        vboxDetail.Add(vboxTitle, 0, wx.ALIGN_CENTER | wx.TOP, 20)
        vboxDetail.Add(self.displayBox, 0, wx.ALIGN_CENTER | wx.ALL, 20)
        self.SetSizer(self.vboxOuter)
        self.detailPan.SetSizer(vboxDetail)

    def showDetails(self):
        self.nameLabel.SetLabel("Name: " + self.network.name)
        self.portLabel.SetLabel("Port: " + str(self.network.port))
        self.baudrateLabel.SetLabel("Baudrate: " + str(self.network.baudrate))
        self.bytesizeLabel.SetLabel("Bytesize: " + str(self.network.bytesize))
        self.parityLabel.SetLabel("Parity: " + str(self.network.parity))
        self.stopbitsLabel.SetLabel("Stopbits: " + str(self.network.stopbits))
        self.timeoutLabel.SetLabel("Timeout: " + str(self.network.timeout))
        self.displayBox.Show(self.networkDetailBoxSizer)
        self.displayBox.Hide(self.networkDataBoxSizer)
        self.Layout()

    def showData(self, data, deviceName):
        self.deviceNameLabel.SetLabel("Device: " + deviceName)
        self.condRes1Label.SetLabel("Cond/Res1: " + str(data.COND_RES1))
        self.condRes1TempLabel.SetLabel("Cond/Res1 Temp: " + str(data.COND_RES1_TEMP))
        self.condRes2Label.SetLabel("Cond/Res2: " + str(data.COND_RES2))
        self.condRes2TempLabel.SetLabel("Cond/Res2 Temp: " + str(data.COND_RES2_TEMP))
        self.phORPLabel.SetLabel("pH/ORP: " + str(data.PH_ORP))
        self.phORPTempLabel.SetLabel("pH/ORP Temp: " + str(data.PH_ORP_TEMP))
        self.displayBox.Hide(self.networkDetailBoxSizer)
        self.displayBox.Show(self.networkDataBoxSizer)
        self.Layout()

    def OnUpdate(self, event):
        testNetwork = 0
        testDeviceIndex = 0
        testNode = [0, self.devicesNode, 0, 0]
        testValue = 3.3
        self.tree.updateNodeFamily(testNetwork, testDeviceIndex, "COND_RES1", testNode, testValue)

    def OnDisplayCellData(self, event):
        self.generateFrames()

    def on_new_frame(self, id, title, position):
        self._parent.panelFrames.append(
            DeviceFrame(self.network, id, title, parent=self, root=self._parent, position=position))

    def ToolBarExitToMainMenu(self):
        self.deviceResponders = []
        self.closeFrames()

    def GoToMainMenu(self, event):
        self._parent.OnMainMenu()

    def closeFrames(self):
        wx.CallAfter(Publisher.sendMessage, "closeCharts")
        self.readingValues = False
        self._parent.currentInstruments = []
        for frame in self._parent.panelFrames:
            frame.getReadyForClose()
            if frame:
                frame.Destroy()
        self._parent.panelFrames = []

    def closeAndGoHome(self):
        self.closeFrames()
        self._parent.OnHome(None)

    def loadView(self, network):
        self.isNetworkLive = False
        self.network = network
        self.networkDevices = self._parent.updateDevicesForSelectedNetwork(self.network)
        # intitalize live data dictionary
        self.liveData = {}
        self.liveData["COND_RES1"] = "NA"
        self.liveData["COND_RES1_TEMP"] = "NA"
        self.liveData["COND_RES2"] = "NA"
        self.liveData["COND_RES2_TEMP"] = "NA"
        self.liveData["PH_ORP"] = "NA"
        self.liveData["PH_ORP_TEMP"] = "NA"
        self.generateTree()

    def refreshView(self, deviceId, deviceIndex):
        for network in self._parent.activeNetworks:
            if network.network.id == self.network.id:
                if deviceId in network.configDataStreams:
                    self.refreshData_labels(network.dataDataStreams[deviceId], network.configDataStreams[deviceId],
                                            deviceIndex)
                    break

    def refreshData_labels(self, dataArray, configDictionary, deviceIndex):
        if dataArray is not None and configDictionary is not None:
            dataCOND_RES1 = dataArray[0]
            if dataCOND_RES1 is not None and float(dataCOND_RES1):
                unit = configDictionary['COND/RES1']['MeasurementUnit']
                cond1Meas = format(float(dataCOND_RES1), '.4f') + " " + unit
                nodeFamily = [self.networkNode, self.devicesNode, deviceIndex, self.liveDataNode]
                self.tree.updateNodeFamily(self.networkNode, deviceIndex, "COND_RES1", nodeFamily, cond1Meas)

            dataCOND_RES1_TEMP = dataArray[1]
            if dataCOND_RES1_TEMP is not None and float(dataCOND_RES1_TEMP):
                unit = configDictionary['COND/RES1']['TemperatureUnit']
                cond1Temp = format(float(dataCOND_RES1_TEMP), '.4f') + " " + unit
                nodeFamily = [self.networkNode, self.devicesNode, deviceIndex, self.liveDataNode]
                self.tree.updateNodeFamily(self.networkNode, deviceIndex, "COND_RES1_TEMP", nodeFamily, cond1Temp)

            dataCOND_RES2 = dataArray[2]
            if dataCOND_RES2 is not None and float(dataCOND_RES2):
                unit = configDictionary['COND/RES2']['MeasurementUnit']
                cond2Meas = format(float(dataCOND_RES2), '.4f') + " " + unit
                nodeFamily = [self.networkNode, self.devicesNode, deviceIndex, self.liveDataNode]
                self.tree.updateNodeFamily(self.networkNode, deviceIndex, "COND_RES2", nodeFamily, cond2Meas)

            dataCOND_RES2_TEMP = dataArray[3]
            if dataCOND_RES2_TEMP is not None and float(dataCOND_RES2_TEMP):
                unit = configDictionary['COND/RES2']['TemperatureUnit']
                cond2Temp = format(float(dataCOND_RES2_TEMP), '.4f') + " " + unit
                nodeFamily = [self.networkNode, self.devicesNode, deviceIndex, self.liveDataNode]
                self.tree.updateNodeFamily(self.networkNode, deviceIndex, "COND_RES2_TEMP", nodeFamily, cond2Temp)

            dataPH_ORP = dataArray[4]
            if dataPH_ORP is not None and float(dataPH_ORP):
                unit = configDictionary['PH/ORP']['MeasurementUnit']
                phORPMeas = format(float(dataPH_ORP), '.4f') + " " + unit
                nodeFamily = [self.networkNode, self.devicesNode, deviceIndex, self.liveDataNode]
                self.tree.updateNodeFamily(self.networkNode, deviceIndex, "PH_ORP", nodeFamily, phORPMeas)

            dataPH_ORP_TEMP = dataArray[5]
            if dataPH_ORP_TEMP is not None and float(dataPH_ORP_TEMP):
                unit = configDictionary['PH/ORP']['TemperatureUnit']
                phORPTemp = format(float(dataPH_ORP_TEMP), '.4f') + " " + unit
                nodeFamily = [self.networkNode, self.devicesNode, deviceIndex, self.liveDataNode]
                self.tree.updateNodeFamily(self.networkNode, deviceIndex, "PH_ORP_TEMP", nodeFamily, phORPTemp)

    def generateTreeData(self, isNetworkLive):
        networks = []
        devices = []
        detailsNode = Details([self.networkNode, self.detailsNode], self.network.port, self.network.baudrate,
                              self.network.bytesize,
                              self.network.parity, self.network.stopbits, self.network.timeout)
        deviceCount = 0
        for device in self.networkDevices:
            deviceName = device.name
            liveDataNode = LiveData([self.networkNode, self.devicesNode, deviceCount, self.liveDataNode],
                                    self.liveData["COND_RES1"],
                                    self.liveData["COND_RES1_TEMP"],
                                    self.liveData["COND_RES2"],
                                    self.liveData["COND_RES2_TEMP"],
                                    self.liveData["PH_ORP"],
                                    self.liveData["PH_ORP_TEMP"]
                                    )
            deviceNode = Device([self.networkNode, self.devicesNode, deviceCount], deviceName, device.address,
                                liveDataNode)
            devices.append(deviceNode)
            deviceCount += 1
        devicesNode = Devices([self.networkNode, self.devicesNode], devices)
        networkName = self.network.name
        if isNetworkLive:
            networks.append(Network([self.networkNode], networkName, "Online", detailsNode, devicesNode))
        else:
            networks.append(Network([self.networkNode], networkName, "Offline", detailsNode, devicesNode))
        return networks

    def generateTree(self):
        for network in self._parent.activeNetworks:
            if network.network.id == self.network.id:
                self.isNetworkLive = True
                break

        if self.tree is None:
            self.tree = ModbusTree(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                   wx.TR_HAS_BUTTONS)
            self.tree.SetBackgroundColour('#0512D2')
            self.tree.SetForegroundColour('#FFFFFF')
            treeFont = self.tree.GetFont()
            treeFont.PointSize += 2
            treeFont = treeFont.Bold()
            self.tree.SetFont(treeFont)
            self.vboxOuter.Add(self.tree, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)
            self.vboxOuter.Add(self.detailPan, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)
            # initialize tree with network data from database
            self.tree.intitalizeTree(self.generateTreeData(self.isNetworkLive))
        else:
            self.tree.collapseAllAndUpdate(self.generateTreeData(self.isNetworkLive))

        # setup device responder
        self.deviceResponders = []
        if self.isNetworkLive:
            for device in self.networkDevices:
                self.deviceResponders.append(DeviceResponder(self.network, device.id, self, device.index + 1))

        self.Layout()

    def generateFrames(self):
        for device in self.networkDevices:
            title = device.name + " (" + self.network.name + ")"
            self.on_new_frame(device.id, title, device.index + 1)
        self.readingValues = True
