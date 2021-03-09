"""
    Panel for creating model graphs
"""

__version__ = "$Revision: 1.0.0 $"
__author__ = "Wayne Smith"
__status__ = "Internal"
__date__ = "08 January 2021"

from ModalGraphFrame import *
from ModalGraphEmbedFrame import *


class DisplayModalGraphPanel(wx.Panel):
    network = None
    networkDevices = []
    devices = []
    sessions = []
    sensorTypes = ['COND/RES1', 'COND/RES2', 'PH/ORP', 'BNC', 'RTD']
    measurementTypes = ["primary", "temp"]
    embedTypes = ['No', 'Yes']
    modalFrames = []
    selectedSession = None
    deviceIndex = 0
    logSessionsForDevice = []
    isLiveModeInList = False
    root = None

    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)
        self.SetBackgroundColour('#000237')
        vboxOuter = wx.BoxSizer(wx.VERTICAL)
        self.vboxInner = wx.BoxSizer(wx.VERTICAL)
        vboxTitle = wx.BoxSizer(wx.VERTICAL)
        self._parent = parent

        midPan = wx.Panel(self)
        midPan.SetBackgroundColour('#0512D2')

        # put some text with a larger bold font on it
        self.title = wx.StaticText(midPan, label="")
        font = self.title.GetFont()
        font.PointSize += 10
        font = font.Bold()
        self.title.SetFont(font)
        self.title.SetForegroundColour('#FFFFFF')
        vboxTitle.Add(self.title, 1, wx.ALIGN_CENTER)

        # graph details sizer box
        graphDetailBox = wx.StaticBox(midPan, -1, 'Graph Details')
        graphDetailBox.SetForegroundColour('#FFFFFF')
        self.graphDetailBoxSizer = wx.StaticBoxSizer(graphDetailBox, wx.VERTICAL)
        self.entryBox = wx.BoxSizer(wx.VERTICAL)

        nameLabel = wx.StaticText(midPan, -1, "Name:")
        nameFont = nameLabel.GetFont()
        nameFont.PointSize += 2
        nameFont = nameFont.Bold()
        nameLabel.SetFont(nameFont)
        nameLabel.SetForegroundColour('#FFFFFF')

        self.entryBox.Add(nameLabel, 1, wx.ALL | wx.CENTER, 5)
        self.titleEntry = wx.TextCtrl(midPan, -1, style=wx.ALIGN_LEFT)
        self.entryBox.Add(self.titleEntry, 0, wx.TOP | wx.BOTTOM | wx.EXPAND, 5)

        deviceLabel = wx.StaticText(midPan, -1, "Device:")
        deviceFont = deviceLabel.GetFont()
        deviceFont.PointSize += 2
        portFont = deviceFont.Bold()
        deviceLabel.SetFont(portFont)
        deviceLabel.SetForegroundColour('#FFFFFF')

        self.entryBox.Add(deviceLabel, 1, wx.ALL | wx.CENTER, 5)
        self.deviceSelect = wx.ComboBox(midPan, choices=self.devices, style=wx.CB_READONLY)
        self.entryBox.Add(self.deviceSelect, 1, wx.TOP | wx.BOTTOM | wx.EXPAND, 5)

        self.deviceSelect.Bind(wx.EVT_COMBOBOX, self.OnDeviceSelect)
        sessionLabel = wx.StaticText(midPan, -1, "Event:")
        sessionFont = sessionLabel.GetFont()
        sessionFont.PointSize += 2
        sessionFont = sessionFont.Bold()
        sessionLabel.SetFont(sessionFont)
        sessionLabel.SetForegroundColour('#FFFFFF')

        self.entryBox.Add(sessionLabel, 1, wx.ALL | wx.CENTER, 5)
        self.sessionSelect = wx.ComboBox(midPan, choices=self.sessions, style=wx.CB_READONLY)
        self.entryBox.Add(self.sessionSelect, 1, wx.TOP | wx.BOTTOM | wx.EXPAND, 5)

        self.sessionSelect.Bind(wx.EVT_COMBOBOX, self.OnSessionSelect)
        sensorLabel = wx.StaticText(midPan, -1, "Sensor:")
        sensorFont = sensorLabel.GetFont()
        sensorFont.PointSize += 2
        sensorFont = sensorFont.Bold()
        sensorLabel.SetFont(sensorFont)
        sensorLabel.SetForegroundColour('#FFFFFF')

        self.entryBox.Add(sensorLabel, 1, wx.ALL | wx.CENTER, 5)
        self.sensorSelect = wx.ComboBox(midPan, choices=self.sensorTypes, style=wx.CB_READONLY)
        self.entryBox.Add(self.sensorSelect, 1, wx.TOP | wx.BOTTOM | wx.EXPAND, 5)

        measurementLabel = wx.StaticText(midPan, -1, "Measurement:")
        measurementFont = measurementLabel.GetFont()
        measurementFont.PointSize += 2
        measurementFont = measurementFont.Bold()
        measurementLabel.SetFont(measurementFont)
        measurementLabel.SetForegroundColour('#FFFFFF')

        self.entryBox.Add(measurementLabel, 1, wx.ALL | wx.CENTER, 5)
        self.measurementSelect = wx.ComboBox(midPan, choices=self.measurementTypes, style=wx.CB_READONLY)
        self.entryBox.Add(self.measurementSelect, 1, wx.TOP | wx.BOTTOM | wx.EXPAND, 5)

        embedLabel = wx.StaticText(midPan, -1, "Embed:")
        embedFont = embedLabel.GetFont()
        embedFont.PointSize += 2
        embedFont = embedFont.Bold()
        embedLabel.SetFont(embedFont)
        embedLabel.SetForegroundColour('#FFFFFF')

        self.entryBox.Add(embedLabel, 1, wx.ALL | wx.CENTER, 5)
        self.embedSelect = wx.ComboBox(midPan, choices=self.embedTypes, style=wx.CB_READONLY)
        self.entryBox.Add(self.embedSelect, 1, wx.TOP | wx.BOTTOM | wx.EXPAND, 5)

        self.entryBox.AddStretchSpacer()
        self.createBtn = wx.Button(midPan, -1, "Create Graph")
        self.createBtn.Bind(wx.EVT_BUTTON, self.OnCreateClicked)
        self.entryBox.Add(self.createBtn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 20)

        self.graphDetailBoxSizer.Add(self.entryBox, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
        self.vboxInner.Add(vboxTitle, 1, wx.ALIGN_CENTER | wx.TOP, 20)
        self.vboxInner.Add(self.graphDetailBoxSizer, 0, wx.ALIGN_CENTER)
        self.vboxInner.AddStretchSpacer()
        midPan.SetSizer(self.vboxInner)
        vboxOuter.Add(midPan, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)
        self.SetSizer(vboxOuter)

    def loadView(self, network):
        self.network = network
        self.networkDevices = self._parent.updateDevicesForSelectedNetwork(self.network)
        if self.networkDevices.count() > 0:
            self.vboxInner.Show(self.graphDetailBoxSizer)
            self.title.SetLabel(self.network.name)
            self.devices = []
            self.sessions = []
            self.sensorSelect.SetSelection(0)
            self.measurementSelect.SetSelection(0)
            self.embedSelect.SetSelection(0)
            self.titleEntry.SetValue(self.networkDevices[0].name)
            for device in self.networkDevices:
                self.devices.append(device.name)
            self.deviceSelect.SetItems(self.devices)
            if self.devices:
                self.deviceSelect.SetSelection(0)
                # get sessions for device at index 0
                deviceId = self.networkDevices[0].id
                isDeviceIdLive = False
                for network in self._parent.activeNetworks:
                    if self.network.id == network.network.id:
                        isDeviceIdLive = True
                        break
                if isDeviceIdLive:
                    self.isLiveModeInList = True
                    self.sessions.append("Live Mode")
                    self.embedSelect.Disable()
                self.logSessionsForDevice = self._parent.GetLogSessionsForDeviceId(deviceId)
                isCurrentSession = True
                for session in self.logSessionsForDevice:
                    if isCurrentSession:
                        isCurrentSession = False
                        self.sessions.append("Current")
                    else:
                        self.sessions.append(session.date)
            self.resetSessionSelection()
        else:
            self.vboxInner.Hide(self.graphDetailBoxSizer)
            self.title.SetLabel("No Devices in Network")
        self.Layout()

    def OnDeviceSelect(self, event):
        self.sessions = []
        self.deviceIndex = self.devices.index(self.deviceSelect.GetValue())
        self.titleEntry.SetValue(self.networkDevices[self.deviceIndex].name)
        deviceId = self.networkDevices[self.deviceIndex].id
        isDeviceIdLive = False
        for network in self._parent.activeNetworks:
            if self.network.id == network.network.id:
                isDeviceIdLive = True
                break
        if isDeviceIdLive:
            self.isLiveModeInList = True
            self.sessions.append("Live Mode")
            self.embedSelect.Disable()
        self.logSessionsForDevice = self._parent.GetLogSessionsForDeviceId(deviceId)
        isCurrentSession = True
        for session in self.logSessionsForDevice:
            if isCurrentSession:
                isCurrentSession = False
                self.sessions.append("Current")
            else:
                self.sessions.append(session.date)

        self.resetSessionSelection()
        self.Layout()

    def OnSessionSelect(self, event):
        if self.sessionSelect.GetValue() == "Live Mode":
            self.embedSelect.SetValue("No")
            self.embedSelect.Disable()
        else:
            self.sessionSelect.Enable()
            self.embedSelect.Enable()

    def resetSessionSelection(self):
        self.sessionSelect.SetItems(self.sessions)
        if self.sessions:
            self.sessionSelect.SetSelection(0)

    def on_new_frame(self, session, title, sensor, measurement, position, liveMode):
        deviceId = self.networkDevices[self.deviceIndex].id
        if self.embedSelect.GetValue() == "No":
            self.modalFrames.append(ModalGraphFrame(deviceId, self.network, session, title, sensor, measurement, position, liveMode, parent=self, root=self._parent))
        else:
            isSessionPresent = False
            frameIndex = 0
            for frame in self.modalFrames:
                if isinstance(frame, ModalGraphEmbedFrame) and session.id == frame._session.id:
                    isSessionPresent = True
                    break
                frameIndex += 1
            if len(self.modalFrames) == 0 or not isSessionPresent:
                self.modalFrames.append(ModalGraphEmbedFrame(session, title, sensor, measurement, position, liveMode, parent=self, root=self._parent))
            else:
                if len(self.modalFrames[frameIndex].devicePanel.devicePanels) < 4:
                    self.modalFrames[frameIndex].addChart(title, sensor, measurement, position)
                else:
                    self.modalFrames.append(
                        ModalGraphFrame(deviceId, self.network, session, title, sensor, measurement, position, liveMode, parent=self,
                                        root=self._parent))

    def closeFrames(self, frameId=None):
        updatedFrames = []
        for frame in self.modalFrames:
            if frame:
                if id is None or frame.frameId == frameId:
                    frame.getReadyForClose()
                    frame.Destroy()
                elif id is not None:
                    updatedFrames.append(frame)
        if id is None:
            self.modalFrames = []
        else:
            self.modalFrames = updatedFrames

    def ToolBarExitToMainMenu(self):
        self.closeFrames()

    def closeAndGoHome(self, frameId=None):
        self.closeFrames(frameId)

    def OnCreateClicked(self, event):
        title = self.titleEntry.GetValue() + " (" + self.network.name + ")"
        if self.sessions and title != "":
            sessionIndex = self.sessions.index(self.sessionSelect.GetValue())
            if self.isLiveModeInList:
                sessionIndex -= 1
            session = self.logSessionsForDevice[sessionIndex]
            sensor = self.sensorSelect.GetValue()
            measurement = self.measurementSelect.GetValue()
            self.on_new_frame(session, title, sensor, measurement, self.deviceIndex + 1, self.sessionSelect.GetValue() == "Live Mode")

    def GoToMainMenu(self, event):
        self._parent.OnMainMenu()
