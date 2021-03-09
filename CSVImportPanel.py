"""
    Panel for importing ranch data to database
"""

__version__ = "$Revision: 1.0.0 $"
__author__ = "Wayne Smith"
__status__ = "Internal"
__date__ = "18 January 2021"

import wx
import csv
from Database import *
import datetime


class CSVImportPanel(wx.Panel):

    devices = []
    sessions = []
    networks = []
    logSessionsForDevice = []
    deviceIndex = 0
    sessionIndex = 0
    dataToStore = []
    network = None

    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)

        self.SetBackgroundColour('#000237')
        vboxOuter = wx.BoxSizer(wx.VERTICAL)
        vboxInner = wx.BoxSizer(wx.VERTICAL)
        vboxTitle = wx.BoxSizer(wx.VERTICAL)
        vboxMenu = wx.BoxSizer(wx.VERTICAL)
        vboxControls = wx.BoxSizer(wx.VERTICAL)
        self._parent = parent

        midPan = wx.Panel(self)
        midPan.SetBackgroundColour('#0512D2')

        title = wx.StaticText(midPan, label="CSV: Import")
        font = title.GetFont()
        font.PointSize += 10
        font = font.Bold()
        title.SetFont(font)
        title.SetForegroundColour('#FFFFFF')

        exportCSVBox = wx.StaticBox(midPan, -1, 'CSV to Database')
        exportCSVBox.SetForegroundColour('#FFFFFF')
        exportCSVBoxSizer = wx.StaticBoxSizer(exportCSVBox, wx.VERTICAL)

        self.inputBox = wx.BoxSizer(wx.VERTICAL)

        networkLabel = wx.StaticText(midPan, -1, "Network:")
        networkFont = networkLabel.GetFont()
        networkFont.PointSize += 2
        networkFont = networkFont.Bold()
        networkLabel.SetFont(networkFont)
        networkLabel.SetForegroundColour('#FFFFFF')

        self.inputBox.Add(networkLabel, 1, wx.ALL | wx.CENTER, 5)
        self.networkSelect = wx.ComboBox(midPan, choices=self.networks, style=wx.CB_READONLY)
        self.inputBox.Add(self.networkSelect, 1, wx.TOP | wx.BOTTOM | wx.EXPAND, 5)
        self.networkSelect.Bind(wx.EVT_COMBOBOX, self.OnNetworkSelect)

        deviceLabel = wx.StaticText(midPan, -1, "Device:")
        deviceFont = deviceLabel.GetFont()
        deviceFont.PointSize += 2
        portFont = deviceFont.Bold()
        deviceLabel.SetFont(portFont)
        deviceLabel.SetForegroundColour('#FFFFFF')

        self.inputBox.Add(deviceLabel, 1, wx.ALL | wx.CENTER, 5)
        self.deviceSelect = wx.ComboBox(midPan, choices=self.devices, style=wx.CB_READONLY)
        self.inputBox.Add(self.deviceSelect, 1, wx.TOP | wx.BOTTOM | wx.EXPAND, 5)
        self.deviceSelect.Bind(wx.EVT_COMBOBOX, self.OnDeviceSelect)

        sessionLabel = wx.StaticText(midPan, -1, "Event:")
        sessionFont = sessionLabel.GetFont()
        sessionFont.PointSize += 2
        sessionFont = sessionFont.Bold()
        sessionLabel.SetFont(sessionFont)
        sessionLabel.SetForegroundColour('#FFFFFF')

        self.inputBox.Add(sessionLabel, 1, wx.ALL | wx.CENTER, 5)
        self.sessionSelect = wx.ComboBox(midPan, choices=self.sessions, style=wx.CB_READONLY)
        self.inputBox.Add(self.sessionSelect, 1, wx.TOP | wx.BOTTOM | wx.EXPAND, 5)

        self.controlBox = wx.BoxSizer(wx.VERTICAL)
        inputLabel = wx.StaticText(midPan, -1, "Input File:")
        inputFont = inputLabel.GetFont()
        inputFont.PointSize += 2
        inputFont = inputFont.Bold()
        inputLabel.SetFont(inputFont)
        inputLabel.SetForegroundColour('#FFFFFF')

        self.controlBox.Add(inputLabel, 0, wx.ALL | wx.CENTER, 5)
        self.inputEntry = wx.TextCtrl(midPan)
        self.controlBox.Add(self.inputEntry, 0, wx.TOP | wx.BOTTOM | wx.EXPAND, 5)

        self.inputButton = wx.Button(midPan, -1, "Import")
        self.inputButton.Bind(wx.EVT_BUTTON, self.CSVToDatabase)
        self.controlBox.Add(self.inputButton, 0, wx.TOP | wx.BOTTOM | wx.EXPAND, 5)

        groupSizer = wx.BoxSizer(wx.HORIZONTAL)
        groupSizer.Add(self.inputBox, 0, wx.ALL, 10)
        groupSizer.Add(self.controlBox, 0, wx.ALL, 10)

        exportCSVBoxSizer.Add(groupSizer, 0, wx.EXPAND | wx.ALL, 20)
        buttonsBox = wx.StaticBox(midPan, -1, 'MENU')
        buttonsBox.SetForegroundColour('#FFFFFF')
        buttonsBoxSizer = wx.StaticBoxSizer(buttonsBox, wx.VERTICAL)
        buttonsSizer = wx.BoxSizer(wx.VERTICAL)

        self.btnHome = wx.Button(midPan, -1, "Main Menu")
        buttonsSizer.Add(self.btnHome, 0, wx.EXPAND | wx.ALL, 10)
        self.btnHome.Bind(wx.EVT_BUTTON, self.GoToMainMenu)
        buttonsBoxSizer.Add(buttonsSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 50)

        vboxTitle.Add(title, 1, wx.ALIGN_CENTER)
        vboxMenu.Add(buttonsBoxSizer, 1, wx.ALIGN_CENTER)
        vboxControls.Add(exportCSVBoxSizer, 1, wx.ALIGN_CENTER)

        groupSizer = wx.BoxSizer(wx.VERTICAL)
        groupSizer.Add(vboxControls, 0, wx.EXPAND | wx.ALL, 10)
        groupSizer.Add(vboxMenu, 0, wx.EXPAND | wx.ALL, 10)

        vboxInner.Add(vboxTitle, 0, wx.ALIGN_CENTER | wx.TOP, 20)
        vboxInner.AddStretchSpacer()
        vboxInner.Add(groupSizer, 0, wx.ALIGN_CENTER)
        vboxInner.AddStretchSpacer()

        midPan.SetSizer(vboxInner)
        vboxOuter.Add(midPan, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)
        self.SetSizer(vboxOuter)

    def GoToMainMenu(self, event):
        self._parent.OnMainMenu()

    def updateSessions(self):
        devices = self._parent.getDevicesForSelectedNetwork(self.network.id)
        deviceId = devices[self.deviceIndex].id
        self.logSessionsForDevice = self._parent.GetLogSessionsForDeviceId(deviceId)
        for session in self.logSessionsForDevice:
            self.sessions.append(session.date)

    def OnDeviceSelect(self, event):
        self.sessions = []
        self.sessions.append("New Session")
        self.deviceIndex = self.devices.index(self.deviceSelect.GetValue())
        self.updateSessions()
        self.sessionSelect.SetItems(self.sessions)
        self.sessionSelect.SetSelection(0)
        self.Layout()

    def OnNetworkSelect(self, event):
        self.devices = []
        self.updateNetwork()

    def loadView(self):
        self.networks = []
        self.devices = []
        self.sessions = []
        self.inputEntry.SetLabel("")
        for network in self._parent.networks:
            self.networks.append(network.name)
        self.networkSelect.SetItems(self.networks)
        if self.networks:
            self.networkSelect.SetSelection(0)
            self.updateNetwork()

    def updateNetwork(self):
        selectedNetwork = self.networkSelect.GetValue()
        for network in self._parent.networks:
            if network.name == selectedNetwork:
                self.network = network
                break
        devices = self._parent.updateDevicesForSelectedNetwork(self.network)
        for device in devices:
            self.devices.append(device.name)
        self.deviceSelect.SetItems(self.devices)
        self.sessions = []
        self.sessions.append("New Session")
        if self.devices:
            self.deviceSelect.SetSelection(0)
            self.deviceIndex = self.devices.index(self.deviceSelect.GetValue())
            self.updateSessions()
        self.sessionSelect.SetItems(self.sessions)
        self.sessionSelect.SetSelection(0)
        self.Layout()

    def CSVToDatabase(self, event):
        inputFileName = self.inputEntry.GetValue()
        self.inputEntry.SetLabel("")
        if inputFileName != "":
            csv_file = ROOT_DIR + "\\" + inputFileName + ".csv"
            fileObj = open(csv_file)
            reader = csv.reader(fileObj)
            self.dataToStore = []
            for row in reader:
                if row[1] == "RANCH1":
                    time = datetime.datetime.strptime(row[0], "%m/%d/%y %H:%M:%S")
                    time = time.strftime("%Y-%m-%d %H:%M:%S")
                    condRes1Value = row[2]
                    condRes1Unit = row[3]
                    condRes1Temp = row[4]
                    condRes1tempUnit = row[5]
                    condRes2Value = row[6]
                    condRes2Unit = row[7]
                    condRes2Temp = row[8]
                    condRes2tempUnit = row[9]
                    phOrpValue = row[10]
                    phOrpUnit = row[11]
                    phOrpTemp = row[12]
                    phOrpTempUnit = row[13]
                    if condRes1Value != "NA":
                        self.dataToStore.append(
                            {"sensorType": 'COND/RES1', "measurementType": "primary", "time": time, "value": float(condRes1Value)})
                    if condRes1Temp != "NA":
                        self.dataToStore.append(
                        {"sensorType": 'COND/RES1', "measurementType": "temp", "time": time, "value": float(condRes1Temp)})
                    if condRes2Value != "NA":
                        self.dataToStore.append(
                        {"sensorType": 'COND/RES2', "measurementType": "primary", "time": time, "value": float(condRes2Value)})
                    if condRes2Temp != "NA":
                        self.dataToStore.append(
                        {"sensorType": 'COND/RES2', "measurementType": "temp", "time": time, "value": float(condRes2Temp)})
                    if phOrpValue != "NA":
                        self.dataToStore.append(
                        {"sensorType": 'PH/ORP', "measurementType": "primary", "time": time, "value": float(phOrpValue)})
                    if phOrpTemp != "NA":
                        self.dataToStore.append(
                        {"sensorType": 'PH/ORP', "measurementType": "temp", "time": time, "value": float(phOrpTemp)})


            #create new session or get selected session
            sessionIndex = self.sessions.index(self.sessionSelect.GetValue())
            if sessionIndex == 0:
                sessionId = self._parent.GetNextLogSessionId()
                self.deviceIndex = self.devices.index(self.deviceSelect.GetValue())
                devices = self._parent.getDevicesForSelectedNetwork(self.network.id)
                deviceId = devices[self.deviceIndex].id
                self._parent.CreateNewSession(deviceId,
                                                           "",
                                                           "",
                                                           "",
                                                           condRes1Unit,
                                                           condRes1tempUnit,
                                                           "",
                                                           "",
                                                           "",
                                                           condRes2Unit,
                                                           condRes2tempUnit,
                                                           "",
                                                           "",
                                                           phOrpUnit,
                                                           phOrpTempUnit,
                                                           "",
                                                           "",
                                                           "",
                                                           "")
            else:
                sessionId = self.logSessionsForDevice[sessionIndex - 1].id

            #generate LogSessionMeasurement
            self._parent.CreateLogRecord(self.dataToStore[0]["time"], self.dataToStore[len(self.dataToStore) - 1]["time"], self.dataToStore, sessionId)

            if self.sessionSelect.GetValue() == "New Session":
                self.sessions = []
                self.sessions.append("New Session")
                self.updateSessions()
                self.sessionSelect.SetItems(self.sessions)
                self.sessionSelect.SetSelection(1)
                self.Layout()
