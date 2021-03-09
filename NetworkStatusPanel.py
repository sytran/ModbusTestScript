"""
    Panel for controlling network status
"""

__version__ = "$Revision: 1.0.0 $"
__author__ = "Wayne Smith"
__status__ = "Internal"
__date__ = "27 January 2021"

import wx
import threading
from wx.lib.agw import ultimatelistctrl as ULC
from wx.lib.pubsub import pub as Publisher
import time
from Utilities import *
import minimalmodbus
import serial.tools.list_ports
import datetime


class DeviceResponder:
    connectedDevice = None
    condRes1Measurement = None
    condRes1Temp = None
    condRes2Measurement = None
    condRes2Temp = None
    pHORPMeasurement = None
    pHORPTemp = None
    bncMeasurement = None
    rtdMeasurement = None
    logSessionId = None

    def __init__(self, parent, root, deviceId, network, position, device):
        self.dataList = []
        self.devicePosition = position
        self.network = network
        self.connectedDevice = device
        self.root = root
        self._parent = parent
        self.deviceId = deviceId
        self.position = position
        messageData = "refreshData" + str(network.id) + str(position)
        Publisher.subscribe(self.refreshData, messageData)
        configData = "refreshConfig" + str(network.id) + str(position)
        Publisher.subscribe(self.refreshConfig, configData)
        messageRelaysAlarms = "refreshRelaysAlarms" + str(network.id) + str(position)
        Publisher.subscribe(self.refreshRelaysAlarms, messageRelaysAlarms)
        messageStoreData = "logData" + str(network.id) + str(position)
        Publisher.subscribe(self.logData, messageStoreData)

    def refreshData(self):

        self._parent.dataDataStreams[self.deviceId] = self.connectedDevice.read_registers(
            registeraddress=DATA_REGISTER_START,
            number_of_registers=30,
            functioncode=MODBUS_FUNCTION_DATA_REGISTERS,

            number_of_values=DATA_VALUES_COUNT)

    def refreshRelaysAlarms(self):
        self._parent.bitDataStreams[self.deviceId] = self.connectedDevice.read_bits(
            registeraddress=RELAY_ALARM_REGISTER_START,
            number_of_bits=6,
            functioncode=MODBUS_FUNCTION_RELAYS_ALARMS_REGISTERS)

        # data refresh notification
        message = "refreshView" + str(self.network.id) + str(self.position)
        wx.CallAfter(Publisher.sendMessage, message)

    def logData(self):
        if self.network.logging:
            dataCOND_RES1 = self._parent.dataDataStreams[self.deviceId][0]
            if self.condRes1Measurement is None or dataCOND_RES1 != self.condRes1Measurement:
                self.condRes1Measurement = dataCOND_RES1
                self.newDataEntry('COND/RES1', "primary", self.condRes1Measurement)

            dataCOND_RES1_TEMP = self._parent.dataDataStreams[self.deviceId][1]
            if self.condRes1Temp is None or dataCOND_RES1_TEMP != self.condRes1Temp:
                self.condRes1Temp = dataCOND_RES1_TEMP
                self.newDataEntry('COND/RES1', "temp", self.condRes1Temp)

            dataCOND_RES2 = self._parent.dataDataStreams[self.deviceId][2]
            if self.condRes2Measurement is None or dataCOND_RES2 != self.condRes2Measurement:
                self.condRes2Measurement = dataCOND_RES2
                self.newDataEntry('COND/RES2', "primary", self.condRes2Measurement)

            dataCOND_RES2_TEMP = self._parent.dataDataStreams[self.deviceId][3]
            if self.condRes2Temp is None or dataCOND_RES2_TEMP != self.condRes2Temp:
                self.condRes2Temp = dataCOND_RES2_TEMP
                self.newDataEntry('COND/RES2', "temp", self.condRes2Temp)

            dataPH_ORP = self._parent.dataDataStreams[self.deviceId][4]
            if self.pHORPMeasurement is None or dataPH_ORP != self.pHORPMeasurement:
                self.pHORPMeasurement = dataPH_ORP
                self.newDataEntry('PH/ORP', "primary", self.pHORPMeasurement)

            dataPH_ORP_TEMP = self._parent.dataDataStreams[self.deviceId][5]
            if self.pHORPTemp is None or dataPH_ORP_TEMP != self.pHORPTemp:
                self.pHORPTemp = dataPH_ORP_TEMP
                self.newDataEntry('PH/ORP', "temp", self.pHORPTemp)

            dataBNC = self._parent.dataDataStreams[self.deviceId][6]
            if self.bncMeasurement is None or dataBNC != self.bncMeasurement:
                self.bncMeasurement = dataBNC
                self.newDataEntry('BNC', "primary", self.bncMeasurement)

            dataRTD = self._parent.dataDataStreams[self.deviceId][7]
            if self.rtdMeasurement is None or dataRTD != self.rtdMeasurement:
                self.rtdMeasurement = dataRTD
                self.newDataEntry('RTD', "primary", self.rtdMeasurement)

    def newDataEntry(self, sensorType, measurementType, value):

        currentTime = datetime.datetime.now()
        self._parent.liveDataStreams[self.deviceId].append(
            {"sensorType": sensorType, "measurementType": measurementType,
             "time": currentTime.strftime("%Y-%m-%d %H:%M:%S"), "value": value})

        listSize = len(self._parent.liveDataStreams[self.deviceId]) - 1
        for _ in range(listSize):
            firstLiveMeasurement = self._parent.liveDataStreams[self.deviceId][0]["time"]
            liveTime = currentTime - datetime.datetime.strptime(firstLiveMeasurement, TIME_FMT)
            if liveTime.total_seconds() > RECORD_INTERVAL:
                self.dataList.append(self._parent.liveDataStreams[self.deviceId].pop(0))
            else:
                break

        if self.dataList:
            firstStoredMeasurement = self.dataList[0]["time"]
            recentStoredMeasurement = self.dataList[len(self.dataList) - 1]["time"]
            storedTime = datetime.datetime.strptime(recentStoredMeasurement, TIME_FMT) - datetime.datetime.strptime(
                firstStoredMeasurement, TIME_FMT)
            if storedTime.total_seconds() > RECORD_INTERVAL:
                # create new data record
                self.root.CreateLogRecord(self.dataList[0]["time"],
                                          self.dataList[len(self.dataList) - 1]["time"], self.dataList,
                                          self.logSessionId)
                # clear data list
                self.dataList = []

    def logFinalData(self):
        if self.network.logging:
            backUpList = self.dataList
            for measurement in self._parent.liveDataStreams[self.deviceId]:
                backUpList.append(measurement)
            self.dataList = []
            # create new data record
            self.root.CreateLogRecord(backUpList[0]["time"],
                                      backUpList[len(backUpList) - 1]["time"], backUpList,
                                      self.logSessionId)

    def refreshConfig(self):
        configDictionary = self.getDataConfig()
        self._parent.configDataStreams[self.deviceId] = configDictionary
        if self.network.logging:
            # create New Session
            self.logSessionId = self.root.GetNextLogSessionId()
            self.dataList = []
            self.root.CreateNewSession(self.network, self.deviceId,
                                       configDictionary['COND/RES1']['MeasurementType'],
                                       configDictionary['COND/RES1']['SolutionType'],
                                       configDictionary['COND/RES1']['ProbeType'],
                                       configDictionary['COND/RES1']['MeasurementUnit'],
                                       configDictionary['COND/RES1']['TemperatureUnit'],
                                       configDictionary['COND/RES2']['MeasurementType'],
                                       configDictionary['COND/RES2']['SolutionType'],
                                       configDictionary['COND/RES2']['ProbeType'],
                                       configDictionary['COND/RES2']['MeasurementUnit'],
                                       configDictionary['COND/RES2']['TemperatureUnit'],
                                       configDictionary['PH/ORP']['MeasurementType'],
                                       configDictionary['PH/ORP']['ProbeType'],
                                       configDictionary['PH/ORP']['MeasurementUnit'],
                                       configDictionary['PH/ORP']['TemperatureUnit'],
                                       configDictionary['BNC']['MeasurementType'],
                                       configDictionary['BNC']['ProbeType'],
                                       configDictionary['RTD']['MeasurementType'],
                                       configDictionary['RTD']['ProbeType'])

    def getDataConfig(self):
        registerData = self.connectedDevice.read_registers(registeraddress=DATA_REGISTER_START,
                                                           number_of_registers=30,
                                                           functioncode=MODBUS_FUNCTION_CONFIG_REGISTERS,
                                                           number_of_values=DATA_VALUES_COUNT,
                                                           is_float=False)
        configDictionary = {}
        for i in range(len(registerData)):
            configDictionaryValues = {}
            binaryString = format(registerData[i], '032b')

            # get first four bits (Sensor Type)
            sensorType = str(int(binaryString[0:4], 2)).encode('utf8')
            configDictionaryValues['SensorType'] = sensorTypeDescription(sensorType)

            # get following five bits (Probe Type)
            probeType = str(int(binaryString[4:9], 2)).encode('utf8')
            if i > 3:
                configDictionaryValues['ProbeType'] = probeTypeDescription(probeType)
            else:
                configDictionaryValues['ProbeType'] = probeTypeDescription(probeType, isCOND=True)

            # get following four bits (Measurement Type)
            measurementType = str(int(binaryString[9:13], 2)).encode('utf8')
            configDictionaryValues['MeasurementType'] = measurementTypeDescription(measurementType)

            # get following three bits (Solution Type)
            solutionType = str(int(binaryString[13:16], 2)).encode('utf8')
            configDictionaryValues['SolutionType'] = solutionTypeDescription(solutionType)

            # get following five bits (Measurement Unit)
            measurementUnit = str(int(binaryString[16:21], 2)).encode('utf8')
            configDictionaryValues['MeasurementUnit'] = measurementUnitDescription(measurementUnit)

            # get following five bits (Relay/Alarm Identification)
            relayAlarmIdentification = binaryString[21:26]
            configDictionaryValues['RelayAlarmIdentification'] = relayAlarmIdentification

            # get the following one bit (Relay/Alarm Enable)
            relayAlarmEnable = binaryString[26:27]
            if relayAlarmEnable:
                configDictionaryValues['RelayAlarmEnable'] = "Enabled"
            else:
                configDictionaryValues['RelayAlarmEnable'] = "Disabled"

            # get following five bits (Temperature Unit)
            temperatureUnit = str(int(binaryString[27:32], 2)).encode('utf8')
            configDictionaryValues['TemperatureUnit'] = measurementUnitDescription(temperatureUnit)

            if i == 0:
                configDictionary['COND/RES1'] = configDictionaryValues
            elif i == 2:
                configDictionary['COND/RES2'] = configDictionaryValues
            elif i == 4:
                configDictionary['PH/ORP'] = configDictionaryValues
            elif i == 6:
                configDictionary['BNC'] = configDictionaryValues
            elif i == 7:
                configDictionary['RTD'] = configDictionaryValues

        return configDictionary


class ActiveNetwork:
    readingValues = True
    workerThread = None
    deviceResponders = []
    liveDataStreams = {}
    configDataStreams = {}
    dataDataStreams = {}
    bitDataStreams = {}

    def __init__(self, root, parent, network):
        self.root = root
        self._parent = parent
        self.network = network
        self.createWorkerThread()

    def createWorkerThread(self):
        self.workerThread = threading.Thread(target=self.readValues, args=())
        self.workerThread.daemon = True
        self.workerThread.start()

    def readValues(self):
        time.sleep(READ_INTERVAL)
        # get config values
        # current instruments for network
        devices = self.root.getDevicesForSelectedNetwork(self.network.id)
        for device in devices:
            position = device.index + 1
            port = self._parent.find_com_port(self.network)
            # instrument set-up
            newInstrument = minimalmodbus.Instrument(port, position, mode=minimalmodbus.MODE_RTU)
            # serial properties
            newInstrument.serial.baudrate = self.network.baudrate
            newInstrument.serial.bytesize = self.network.bytesize
            if self.network.parity:
                newInstrument.serial.parity = minimalmodbus.serial.PARITY_ODD
            else:
                newInstrument.serial.parity = minimalmodbus.serial.PARITY_EVEN
            newInstrument.serial.stopbits = self.network.stopbits
            newInstrument.serial.timeout = self.network.timeout

            # message settings
            newInstrument.close_port_after_each_call = True
            newInstrument.clear_buffers_before_each_transaction = True
            self.liveDataStreams[device.id] = []
            self.configDataStreams[device.id] = None
            self.dataDataStreams[device.id] = None
            self.bitDataStreams[device.id] = None
            self.deviceResponders.append(
                DeviceResponder(self, self.root, device.id, self.network, position, newInstrument))

        # get config values
        for i in range(len(self.deviceResponders)):
            message = "refreshConfig" + str(self.network.id) + str(i + 1)
            wx.CallAfter(Publisher.sendMessage, message)
            time.sleep(READ_INTERVAL)
        while self.readingValues:
            for i in range(len(self.deviceResponders)):
                message = "refreshData" + str(self.network.id) + str(i + 1)
                wx.CallAfter(Publisher.sendMessage, message)
                time.sleep(READ_INTERVAL)
                message = "refreshRelaysAlarms" + str(self.network.id) + str(i + 1)
                wx.CallAfter(Publisher.sendMessage, message)
                time.sleep(READ_INTERVAL)
                message = "logData" + str(self.network.id) + str(i + 1)
                wx.CallAfter(Publisher.sendMessage, message)
                time.sleep(DATA_STORAGE_INTERVAL)

        for responder in self.deviceResponders:
            responder.logFinalData()


class NetworkStatusPanel(wx.Panel):
    lastSelectedIndex = None
    boldfont = None
    activeNetworks = []
    isSelectedNetworkConnected = False
    selectedNetwork = None

    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)

        self.SetBackgroundColour('#000237')
        vboxOuter = wx.BoxSizer(wx.VERTICAL)
        vboxInner = wx.BoxSizer(wx.VERTICAL)
        vboxTitle = wx.BoxSizer(wx.VERTICAL)
        vboxControls = wx.BoxSizer(wx.VERTICAL)
        self._parent = parent
        self.boldfont = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD, False, u'Arial')

        self.midPan = wx.Panel(self)
        self.midPan.SetBackgroundColour('#0512D2')

        # put some text with a larger bold font on it
        self.title = wx.StaticText(self.midPan, label="Network Status")
        font = self.title.GetFont()
        font.PointSize += 10
        font = font.Bold()
        self.title.SetFont(font)
        self.title.SetForegroundColour('#FFFFFF')

        buttonsBox = wx.StaticBox(self.midPan, -1, 'MENU')
        buttonsBox.SetForegroundColour('#FFFFFF')
        buttonsBoxSizer = wx.StaticBoxSizer(buttonsBox, wx.VERTICAL)
        buttonsSizer = wx.BoxSizer(wx.VERTICAL)

        self.btnHome = wx.Button(self.midPan, -1, "Main Menu")
        buttonsSizer.Add(self.btnHome, 0, wx.EXPAND | wx.ALL, 10)
        self.btnHome.Bind(wx.EVT_BUTTON, self.GoToMainMenu)

        buttonsBoxSizer.Add(buttonsSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 50)
        vboxTitle.Add(self.title, 1, wx.ALIGN_CENTER)

        # main sizer box
        self.mainBox = wx.StaticBox(self.midPan, 0, 'Networks')
        self.mainBox.SetForegroundColour('#FFFFFF')
        self.mainBox.SetMinSize((1000, 1000))
        mainBoxSizer = wx.StaticBoxSizer(self.mainBox, wx.VERTICAL)

        # primary operations box
        self.operationBox = wx.BoxSizer(wx.VERTICAL)

        # table views
        self.tableBox = wx.BoxSizer(wx.HORIZONTAL)
        self.listA = ULC.UltimateListCtrl(self.midPan, agwStyle=wx.LC_REPORT
                                                                | wx.LC_HRULES)

        self.Bind(ULC.EVT_LIST_ITEM_SELECTED, self.OnItemSelected,
                  self.listA)
        self.tableBox.Add(self.listA, 1, wx.ALL | wx.EXPAND)

        self.editControlBox = wx.BoxSizer(wx.VERTICAL)

        self.networkLabel = wx.StaticText(self.midPan, -1, "")
        networkLabelFont = self.networkLabel.GetFont()
        networkLabelFont.PointSize += 2
        networkLabelFont = networkLabelFont.Bold()
        self.networkLabel.SetFont(networkLabelFont)
        self.networkLabel.SetForegroundColour('#FFFFFF')
        self.editControlBox.Add(self.networkLabel, 1, wx.ALL | wx.CENTER, 5)

        self.statusLabel = wx.StaticText(self.midPan, -1, "Status: Disconnected")
        statusLabelFont = self.statusLabel.GetFont()
        statusLabelFont.PointSize += 2
        statusLabelFont = statusLabelFont.Bold()
        self.statusLabel.SetFont(statusLabelFont)
        self.statusLabel.SetForegroundColour('#FFFFFF')
        self.editControlBox.Add(self.statusLabel, 1, wx.ALL | wx.CENTER, 5)

        self.networkStatusButton = wx.Button(self.midPan, -1, "Connect")
        self.networkStatusButton.Bind(wx.EVT_BUTTON, self.updateNetworkStatus)
        self.editControlBox.Add(self.networkStatusButton, 1, wx.ALL | wx.CENTER, 5)

        self.editNetworkBox = wx.StaticBox(self.midPan, 0, 'Network Status')
        self.editNetworkBox.SetForegroundColour('#FFFFFF')
        editNetworkBoxSizer = wx.StaticBoxSizer(self.editNetworkBox, wx.VERTICAL)
        editNetworkBoxSizer.Add(self.editControlBox, 0, wx.EXPAND | wx.ALL, 10)

        self.groupControlBox = wx.BoxSizer(wx.VERTICAL)
        self.groupControlBox.Add(editNetworkBoxSizer, 0, wx.EXPAND | wx.ALL, 10)

        self.tableBox.Add(self.groupControlBox, 1, wx.ALL | wx.CENTER, 50)
        self.operationBox.Add(self.tableBox, 1, wx.ALL | wx.EXPAND, 0)

        # add content box to main sizer box
        mainBoxSizer.Add(self.operationBox, 0, wx.EXPAND | wx.ALL, 20)

        # group sizer
        groupSizer = wx.BoxSizer(wx.VERTICAL)
        groupSizer.Add(mainBoxSizer, 0, wx.ALIGN_CENTER)
        groupSizer.Add(vboxControls, 0, wx.EXPAND | wx.ALL, 10)

        vboxControls.Add(buttonsBoxSizer, 0, wx.ALIGN_CENTER)

        vboxInner.Add(vboxTitle, 0, wx.ALIGN_CENTER | wx.TOP, 20)
        vboxInner.AddStretchSpacer()
        vboxInner.Add(groupSizer, 0, wx.ALL | wx.EXPAND, 5)
        vboxInner.AddStretchSpacer()

        self.midPan.SetSizer(vboxInner)
        vboxOuter.Add(self.midPan, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)
        self.SetSizer(vboxOuter)

    def resetSelection(self):
        if self._parent.networks > 0:
            self.listA.Select(0)
        else:
            self.lastSelectedIndex = None

    def loadView(self):
        if self._parent.networks.count() > 0:
            self.networkStatusButton.Enable()
            self.tableSetup()
            self.resetSelection()
        else:
            self.networkStatusButton.Disable()

    def tableSetup(self):
        self.listA.ClearAll()
        info = ULC.UltimateListItem()
        info._format = wx.LIST_FORMAT_LEFT
        info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT
        info._image = []
        info._text = "Networks"
        info._font = self.boldfont

        self.listA.InsertColumnInfo(0, info)
        self.listA.SetColumnWidth(0, 475)
        index = 0
        for network in self._parent.networks:
            self.listA.InsertStringItem(index, network.name)
            index += 1
        self.Layout()

    def OnItemSelected(self, event):
        self.lastSelectedIndex = event.m_itemIndex
        self.selectedNetwork = self._parent.networks[self.lastSelectedIndex]
        self.networkLabel.SetLabel(self.selectedNetwork.name)

        networkFound = False
        for network in self._parent.activeNetworks:
            if network.network.id == self.selectedNetwork.id:
                networkFound = True
                break

        if networkFound:
            self.isSelectedNetworkConnected = True
            self.statusLabel.SetLabel("Status: Connected")
            self.networkStatusButton.SetLabel("Disconnect")
        else:
            self.isSelectedNetworkConnected = False
            self.statusLabel.SetLabel("Status: Disconnected")
            self.networkStatusButton.SetLabel("Connect")
        self.Layout()

    def updateNetworkStatus(self, event):
        if not self.isSelectedNetworkConnected:
            self.addActiveNetwork(self.selectedNetwork)
            # update UI
            self.isSelectedNetworkConnected = True
            self.statusLabel.SetLabel("Status: Connected")
            self.networkStatusButton.SetLabel("Disconnect")
        else:
            for i in range(len(self._parent.activeNetworks)):
                if self._parent.activeNetworks[i].network.id == self.selectedNetwork.id:
                    self._parent.activeNetworks[i].readingValues = False
                    del self._parent.activeNetworks[i]
                    break
            # update UI
            self.isSelectedNetworkConnected = False
            self.statusLabel.SetLabel("Status: Disconnected")
            self.networkStatusButton.SetLabel("Connect")
        self.Layout()

    def addActiveNetwork(self, network):
        # create network
        self._parent.activeNetworks.append(ActiveNetwork(self._parent, self, network))

    def find_com_port(self, network):
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            if str(port).startswith("COM" + str(network.port)):
                return port[0]
        return None

    def ToolBarExitToMainMenu(self):
        self.lastSelectedIndex = None

    def GoToMainMenu(self, event):
        self.lastSelectedIndex = None
        self._parent.OnMainMenu()
