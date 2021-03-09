"""
    Panel for creating networks
"""

__version__ = "$Revision: 1.0.0 $"
__author__ = "Wayne Smith"
__status__ = "Internal"
__date__ = "09 December 2020"

import wx
import serial.tools.list_ports


class CreateNetworkPanel(wx.Panel):
    network = None
    networkCreated = False
    isEditMode = None
    parityTypes = ["Even", "Odd"]
    byteSizes = ["8"]
    baudRates = ["9600", "14400", "19200", "38400", "56000", "57600", "115200"]
    ports = []
    stopBits = ["1"]
    timeoutSelections = ["1"]
    loggingSelections = ["No", "Yes"]

    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)
        self.SetBackgroundColour('#000237')
        vboxOuter = wx.BoxSizer(wx.VERTICAL)
        vboxInner = wx.BoxSizer(wx.VERTICAL)
        vboxTitle = wx.BoxSizer(wx.VERTICAL)
        self._parent = parent

        midPan = wx.Panel(self)
        midPan.SetBackgroundColour('#0512D2')

        # put some text with a larger bold font on it
        self.title = wx.StaticText(midPan, label="Create Network")
        font = self.title.GetFont()
        font.PointSize += 10
        font = font.Bold()
        self.title.SetFont(font)
        self.title.SetForegroundColour('#FFFFFF')
        vboxTitle.Add(self.title, 1, wx.ALIGN_CENTER)

        # network detail sizer box
        networkDetailBox = wx.StaticBox(midPan, -1, 'Network Detail')
        networkDetailBox.SetForegroundColour('#FFFFFF')
        networkDetailBoxSizer = wx.StaticBoxSizer(networkDetailBox, wx.VERTICAL)

        self.entryBox = wx.BoxSizer(wx.VERTICAL)
        self.infoLabel = wx.StaticText(midPan, -1, "")
        self.infoFont = self.infoLabel.GetFont()
        self.infoFont.PointSize += 5
        self.infoFont = self.infoFont.Bold()
        self.infoLabel.SetFont(self.infoFont)
        self.entryBox.Add(self.infoLabel, 1, wx.CENTER)

        nameLabel = wx.StaticText(midPan, -1, "Name:")
        nameFont = nameLabel.GetFont()
        nameFont.PointSize += 2
        nameFont = nameFont.Bold()
        nameLabel.SetFont(nameFont)
        nameLabel.SetForegroundColour('#FFFFFF')

        self.entryBox.Add(nameLabel, 1, wx.ALL | wx.CENTER, 5)
        self.nameEntry = wx.TextCtrl(midPan, -1, style=wx.ALIGN_LEFT)
        self.entryBox.Add(self.nameEntry, 0, wx.EXPAND | wx.ALL | wx.CENTER, 5)

        portLabel = wx.StaticText(midPan, -1, "Port:")
        portFont = portLabel.GetFont()
        portFont.PointSize += 2
        portFont = portFont.Bold()
        portLabel.SetFont(portFont)
        portLabel.SetForegroundColour('#FFFFFF')

        self.entryBox.Add(portLabel, 1, wx.ALL | wx.CENTER, 5)
        self.portSelect = wx.ComboBox(midPan, choices=self.ports, style=wx.CB_READONLY)
        self.entryBox.Add(self.portSelect, 0, wx.EXPAND | wx.ALL | wx.CENTER, 5)

        baudrateLabel = wx.StaticText(midPan, -1, "Baudrate:")
        baudrateFont = baudrateLabel.GetFont()
        baudrateFont.PointSize += 2
        baudrateFont = baudrateFont.Bold()
        baudrateLabel.SetFont(baudrateFont)
        baudrateLabel.SetForegroundColour('#FFFFFF')

        self.entryBox.Add(baudrateLabel, 1, wx.ALL | wx.CENTER, 5)
        self.baudrateSelect = wx.ComboBox(midPan, choices=self.baudRates, style=wx.CB_READONLY)
        self.entryBox.Add(self.baudrateSelect, 0, wx.EXPAND | wx.ALL | wx.CENTER, 5)

        bytesizeLabel = wx.StaticText(midPan, -1, "Bytesize:")
        bytesizeFont = bytesizeLabel.GetFont()
        bytesizeFont.PointSize += 2
        bytesizeFont = bytesizeFont.Bold()
        bytesizeLabel.SetFont(bytesizeFont)
        bytesizeLabel.SetForegroundColour('#FFFFFF')

        self.entryBox.Add(bytesizeLabel, 1, wx.ALL | wx.CENTER, 5)
        self.byteSizeSelect = wx.ComboBox(midPan, choices=self.byteSizes, style=wx.CB_READONLY)
        self.entryBox.Add(self.byteSizeSelect, 0, wx.EXPAND | wx.ALL | wx.CENTER, 5)

        parityLabel = wx.StaticText(midPan, -1, "Parity:")
        parityFont = parityLabel.GetFont()
        parityFont.PointSize += 2
        parityFont = bytesizeFont.Bold()
        parityLabel.SetFont(parityFont)
        parityLabel.SetForegroundColour('#FFFFFF')

        self.entryBox.Add(parityLabel, 1, wx.ALL | wx.CENTER, 5)
        self.paritySelect = wx.ComboBox(midPan, choices=self.parityTypes, style=wx.CB_READONLY)
        self.entryBox.Add(self.paritySelect, 0, wx.EXPAND | wx.ALL | wx.CENTER, 5)

        stopbitsLabel = wx.StaticText(midPan, -1, "Stopbits:")
        stopbitsFont = stopbitsLabel.GetFont()
        stopbitsFont.PointSize += 2
        stopbitsFont = stopbitsFont.Bold()
        stopbitsLabel.SetFont(stopbitsFont)
        stopbitsLabel.SetForegroundColour('#FFFFFF')

        self.entryBox.Add(stopbitsLabel, 1, wx.ALL | wx.CENTER, 5)
        self.stopBitsSelect = wx.ComboBox(midPan, choices=self.stopBits, style=wx.CB_READONLY)
        self.entryBox.Add(self.stopBitsSelect, 0, wx.EXPAND | wx.ALL | wx.CENTER, 5)

        timeoutLabel = wx.StaticText(midPan, -1, "Timeout:")
        timeoutFont = timeoutLabel.GetFont()
        timeoutFont.PointSize += 2
        timeoutFont = timeoutFont.Bold()
        timeoutLabel.SetFont(timeoutFont)
        timeoutLabel.SetForegroundColour('#FFFFFF')

        self.entryBox.Add(timeoutLabel, 1, wx.ALL | wx.CENTER, 5)
        self.timeOutSelect = wx.ComboBox(midPan, choices=self.timeoutSelections, style=wx.CB_READONLY)
        self.entryBox.Add(self.timeOutSelect, 0, wx.EXPAND | wx.ALL | wx.CENTER, 5)

        loggingLabel = wx.StaticText(midPan, -1, "Logging:")
        loggingFont = loggingLabel.GetFont()
        loggingFont.PointSize += 2
        loggingFont = loggingFont.Bold()
        loggingLabel.SetFont(loggingFont)
        loggingLabel.SetForegroundColour('#FFFFFF')

        self.entryBox.Add(loggingLabel, 1, wx.ALL | wx.CENTER, 5)
        self.loggingSelect = wx.ComboBox(midPan, choices=self.loggingSelections, style=wx.CB_READONLY)
        self.entryBox.Add(self.loggingSelect, 0, wx.EXPAND | wx.ALL | wx.CENTER, 5)

        self.entryBox.AddStretchSpacer()
        self.createBtn = wx.Button(midPan, -1, "Create")
        self.createBtn.Bind(wx.EVT_BUTTON, self.OnCreateClicked)
        self.entryBox.Add(self.createBtn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 20)

        networkDetailBoxSizer.Add(self.entryBox, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 50)
        vboxInner.Add(vboxTitle, 1, wx.ALIGN_CENTER | wx.TOP, 20)
        vboxInner.AddStretchSpacer()
        vboxInner.Add(networkDetailBoxSizer, 1, wx.ALIGN_CENTER)
        vboxInner.AddStretchSpacer()
        midPan.SetSizer(vboxInner)
        vboxOuter.Add(midPan, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)
        self.SetSizer(vboxOuter)

    def loadView(self, network, isEditMode=False):
        allPorts = list(serial.tools.list_ports.comports())
        self.networkCreated = False
        self.network = network
        self.ports = []
        for port in allPorts:
            if str(port).startswith("COM"):
                self.ports.append(str(port.device))
        self.portSelect.SetItems(self.ports)
        self.portSelect.SetSelection(0)
        self.baudrateSelect.SetSelection(0)
        self.byteSizeSelect.SetSelection(0)
        self.paritySelect.SetSelection(0)
        self.stopBitsSelect.SetSelection(0)
        self.timeOutSelect.SetSelection(0)
        self.loggingSelect.SetSelection(0)
        self.nameEntry.SetValue("")

        self.isEditMode = isEditMode
        if self.isEditMode:
            self.title.SetLabel("Edit Network")
            self.createBtn.SetLabel("Save")
            self.nameEntry.SetValue(self.network.name)
            if ("COM" + str(self.network.port)) in self.ports:
                self.portSelect.SetSelection(self.ports.index("COM" + str(self.network.port)))
            self.baudrateSelect.SetSelection(self.baudRates.index(str(self.network.baudrate)))
            self.byteSizeSelect.SetSelection(self.byteSizes.index(str(self.network.bytesize)))
            self.paritySelect.SetSelection(self.network.parity)
            self.stopBitsSelect.SetSelection(self.stopBits.index(str(self.network.stopbits)))
            self.timeOutSelect.SetSelection(self.timeoutSelections.index(str(self.network.timeout)))
            self.loggingSelect.SetSelection(self.network.logging)
        else:
            self.title.SetLabel("Create Network")
            self.createBtn.SetLabel("Create")

        self.Layout()

    def OnCreateClicked(self, event):

        if self.isEditMode:
            name = self.nameEntry.GetValue()
            port = int(self.portSelect.GetValue()[3:])
            baudrate = int(self.baudrateSelect.GetValue())
            bytesize = int(self.byteSizeSelect.GetValue())
            parity = self.parityTypes.index(self.paritySelect.GetValue())
            stopbits = int(self.stopBitsSelect.GetValue())
            timeout = int(self.timeOutSelect.GetValue())
            logging = 0
            if self.loggingSelect.GetValue() == "Yes":
                logging = 1
            self.network = self._parent.updateNetworkDetails(self.network, name, port, baudrate, bytesize, parity, stopbits, timeout, logging)
            self._parent.showPanelForValue("EditNetworkPanel")
        else:
            if self.networkCreated:
                self.networkCreated = False
                self.infoLabel.SetLabel("")
                self.createBtn.SetLabel("Create")
                self.nameEntry.SetValue("")
                self.portSelect.SetSelection(0)
                self.baudrateSelect.SetSelection(0)
                self.byteSizeSelect.SetSelection(0)
                self.paritySelect.SetSelection(0)
                self.stopBitsSelect.SetSelection(0)
                self.timeOutSelect.SetSelection(0)
                self.loggingSelect.SetSelection(0)
            else:
                name = self.nameEntry.GetValue()
                port = int(self.portSelect.GetValue()[3:])
                baudrate = int(self.baudrateSelect.GetValue())
                bytesize = int(self.byteSizeSelect.GetValue())
                parity = self.parityTypes.index(self.paritySelect.GetValue())
                stopbits = int(self.stopBitsSelect.GetValue())
                timeout = int(self.timeOutSelect.GetValue())
                logging = 0
                if self.loggingSelect.GetValue() == "Yes":
                    logging = 1

                if not (name == "" or port == ""):
                    self._parent.CreateNetwork(name, port, baudrate,
                                               bytesize, parity, stopbits,
                                               timeout, logging)
                    self.networkCreated = True
                    self.infoLabel.SetLabel("Created")
                    self.createBtn.SetLabel("Done")
                    self.Layout()

    def GoToMainMenu(self, event):
        self._parent.OnMainMenu()
