"""
    Panel for editing networks
"""

__version__ = "$Revision: 1.0.0 $"
__author__ = "Wayne Smith"
__status__ = "Internal"
__date__ = "09 December 2020"

import wx
from wx.lib.agw import ultimatelistctrl as ULC


class EditNetworkPanel(wx.Panel):
    network = None
    networkDevices = []
    lastSelectedIndex = None
    boldfont = None
    isNewMode = False

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
        self.title = wx.StaticText(self.midPan, label="")
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
        self.mainBox = wx.StaticBox(self.midPan, 0, 'Network Devices')
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

        # entry views
        self.entryBox = wx.BoxSizer(wx.VERTICAL)

        nameLabel = wx.StaticText(self.midPan, -1, "Name:")
        nameLabelFont = nameLabel.GetFont()
        nameLabelFont.PointSize += 2
        nameLabelFont = nameLabelFont.Bold()
        nameLabel.SetFont(nameLabelFont)
        nameLabel.SetForegroundColour('#FFFFFF')

        self.entryBox.Add(nameLabel, 1, wx.ALL | wx.CENTER, 5)
        self.nameEntry = wx.TextCtrl(self.midPan, -1, style=wx.ALIGN_LEFT)
        self.entryBox.Add(self.nameEntry, 1, wx.ALL | wx.CENTER, 5)

        addressLabel = wx.StaticText(self.midPan, -1, "Address:")
        timeoutFont = addressLabel.GetFont()
        timeoutFont.PointSize += 2
        timeoutFont = timeoutFont.Bold()
        addressLabel.SetFont(timeoutFont)
        addressLabel.SetForegroundColour('#FFFFFF')

        self.entryBox.Add(addressLabel, 1, wx.ALL | wx.CENTER, 5)
        self.addressEntry = wx.TextCtrl(self.midPan, -1, style=wx.ALIGN_LEFT)
        self.entryBox.Add(self.addressEntry, 1, wx.ALL | wx.CENTER, 5)

        # table views
        self.tableControlBox = wx.BoxSizer(wx.VERTICAL)

        self.editDeviceButton = wx.Button(self.midPan, -1, "New")
        self.editDeviceButton.Bind(wx.EVT_BUTTON, self.OnNewDevice)
        self.tableControlBox.Add(self.editDeviceButton, 1, wx.ALL | wx.CENTER, 5)

        self.deleteDeviceButton = wx.Button(self.midPan, -1, "Delete")
        self.deleteDeviceButton.Bind(wx.EVT_BUTTON, self.OnDeleteDevice)
        self.tableControlBox.Add(self.deleteDeviceButton, 1, wx.ALL | wx.CENTER, 5)

        self.moveDeviceUpButton = wx.Button(self.midPan, -1, "Up")
        self.moveDeviceUpButton.Bind(wx.EVT_BUTTON, self.OnMoveDeviceUp)
        self.tableControlBox.Add(self.moveDeviceUpButton, 1, wx.ALL | wx.CENTER, 5)

        self.moveDeviceDownButton = wx.Button(self.midPan, -1, "Down")
        self.moveDeviceDownButton.Bind(wx.EVT_BUTTON, self.OnMoveDeviceDown)
        self.tableControlBox.Add(self.moveDeviceDownButton, 1, wx.ALL | wx.CENTER, 5)

        self.saveButton = wx.Button(self.midPan, -1, "Save")
        self.saveButton.Bind(wx.EVT_BUTTON, self.OnSaveDevice)
        self.tableControlBox.Add(self.saveButton, 1, wx.ALL | wx.CENTER, 5)

        self.groupBox = wx.BoxSizer(wx.HORIZONTAL)
        self.groupBox.Add(self.entryBox, 1, wx.ALL | wx.CENTER, 10)
        self.groupBox.Add(self.tableControlBox, 1, wx.ALL | wx.CENTER, 10)

        self.editControlBox = wx.BoxSizer(wx.VERTICAL)
        self.editNetworkButton = wx.Button(self.midPan, -1, "Edit Network")
        self.editNetworkButton.Bind(wx.EVT_BUTTON, self.GoToEditNetworkDetails)
        self.editControlBox.Add(self.editNetworkButton, 1, wx.ALL | wx.CENTER, 5)

        self.editNetworkBox = wx.StaticBox(self.midPan, 0, 'Edit Network')
        self.editNetworkBox.SetForegroundColour('#FFFFFF')
        editNetworkBoxSizer = wx.StaticBoxSizer(self.editNetworkBox, wx.VERTICAL)
        editNetworkBoxSizer.Add(self.editControlBox, 0, wx.EXPAND | wx.ALL, 10)

        self.networkBox = wx.StaticBox(self.midPan, 0, 'Edit Network Devices')
        self.networkBox.SetForegroundColour('#FFFFFF')
        networkBoxBoxSizer = wx.StaticBoxSizer(self.networkBox, wx.VERTICAL)
        networkBoxBoxSizer.Add(self.groupBox, 0, wx.EXPAND | wx.ALL, 10)

        self.groupControlBox = wx.BoxSizer(wx.VERTICAL)
        self.groupControlBox.Add(editNetworkBoxSizer, 0, wx.EXPAND | wx.ALL, 10)
        self.groupControlBox.Add(networkBoxBoxSizer, 0, wx.EXPAND | wx.ALL, 10)

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
        if self.networkDevices.count() > 0:
            self.listA.Select(0)
        else:
            self.lastSelectedIndex = None
            self.nameEntry.SetValue("")
            self.addressEntry.SetValue("")

    def loadView(self, network):
        self.network = network
        self.title.SetLabel(self.network.name)
        self.networkDevices = self._parent.updateDevicesForSelectedNetwork(self.network)
        self.tableSetup()
        self.resetSelection()

    def tableSetup(self):
        self.listA.ClearAll()
        info = ULC.UltimateListItem()
        info._format = wx.LIST_FORMAT_LEFT
        info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT
        info._image = []
        info._text = "Devices"
        info._font = self.boldfont

        infoPosition = ULC.UltimateListItem()
        infoPosition._format = wx.LIST_FORMAT_LEFT
        infoPosition._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_FONT
        infoPosition._image = []
        infoPosition._text = "Position"
        infoPosition._font = self.boldfont

        self.listA.InsertColumnInfo(0, info)
        self.listA.InsertColumnInfo(1, infoPosition)
        self.listA.SetColumnWidth(0, 350)
        self.listA.SetColumnWidth(1, 125)
        index = 0
        for device in self.networkDevices:
            self.listA.InsertStringItem(index, device.name)
            self.listA.SetStringItem(index, 1, str(device.index + 1))
            index += 1
        self.Layout()

    def GoToEditNetworkDetails(self, event):
        self._parent.showPanelForValue("EditNetworkDetailsPanel")

    def OnItemSelected(self, event):
        self.isNewMode = False
        self.lastSelectedIndex = event.m_itemIndex
        selectedDevice = self.networkDevices[self.lastSelectedIndex]
        self.nameEntry.SetValue(selectedDevice.name)
        self.addressEntry.SetValue(str(selectedDevice.address))

    def OnNewDevice(self, event):
        self.isNewMode = True
        self.nameEntry.SetValue("New Device")
        self.addressEntry.SetValue("")
        self.tableSetup()

    def OnDeleteDevice(self, event):
        if not self.lastSelectedIndex is None:
            shouldResetDeviceIndexValues = False
            if self.networkDevices > 0 and self.networkDevices.count() != self.lastSelectedIndex:
                shouldResetDeviceIndexValues = True
            self._parent.DeleteDevice(self.network, self.lastSelectedIndex)
            if shouldResetDeviceIndexValues:
                for index in range(self.lastSelectedIndex, self.networkDevices.count()):
                    self._parent.UpdateDeviceIndexMatch(self.network, index)
            self.networkDevices = self._parent.updateDevicesForSelectedNetwork(self.network)
            self.tableSetup()
            self.resetSelection()

    def OnMoveDeviceUp(self, event):
        if not self.lastSelectedIndex is None and not self.lastSelectedIndex == 0:
            selectedId = self.networkDevices[self.lastSelectedIndex].id
            deviceAboveId = self.networkDevices[self.lastSelectedIndex - 1].id
            self._parent.UpdateDeviceIndex(selectedId, self.lastSelectedIndex - 1)
            self._parent.UpdateDeviceIndex(deviceAboveId, self.lastSelectedIndex)
            self.networkDevices = self._parent.updateDevicesForSelectedNetwork(self.network)
            self.tableSetup()
            self.listA.Select(self.lastSelectedIndex - 1)

    def OnMoveDeviceDown(self, event):
        if not self.lastSelectedIndex is None and self.lastSelectedIndex < self.networkDevices.count() - 1:
            selectedId = self.networkDevices[self.lastSelectedIndex].id
            deviceBelowId = self.networkDevices[self.lastSelectedIndex + 1].id
            self._parent.UpdateDeviceIndex(selectedId, self.lastSelectedIndex + 1)
            self._parent.UpdateDeviceIndex(deviceBelowId, self.lastSelectedIndex)
            self.networkDevices = self._parent.updateDevicesForSelectedNetwork(self.network)
            self.tableSetup()
            self.listA.Select(self.lastSelectedIndex + 1)

    def OnSaveDevice(self, event):
        name = self.nameEntry.GetValue()
        address = self.addressEntry.GetValue()
        deviceCount = self.networkDevices.count()
        if self.isNewMode or deviceCount == 0:
            self.isNewMode = False
            if not name == "" or address == "":
                self._parent.CreateDevice(name, address, deviceCount, self.network.id)
                self.networkDevices = self._parent.updateDevicesForSelectedNetwork(self.network)
                self.tableSetup()
                self.listA.Select(self.networkDevices.count() - 1)
        else:
            self._parent.UpdateDeviceNameAndAddress(self.network, self.lastSelectedIndex, name, address)
            self.networkDevices = self._parent.updateDevicesForSelectedNetwork(self.network)
            self.tableSetup()
            self.listA.Select(self.lastSelectedIndex)

    def ToolBarExitToMainMenu(self):
        self.lastSelectedIndex = None

    def GoToMainMenu(self, event):
        self.lastSelectedIndex = None
        self._parent.OnMainMenu()
