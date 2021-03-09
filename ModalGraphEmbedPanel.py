"""
    Panel for graphing embedded modal data
"""

__version__ = "$Revision: 1.0.0 $"
__author__ = "Wayne Smith"
__status__ = "Internal"
__date__ = "22 January 2021"

from ModalGraphPanel import *


class ModalGraphEmbedPanel(wx.Panel):
    devicePanels = []
    startIndex = 0
    endIndex = DATA_RANGE
    scaleLocked = False
    timeUnit = SECONDS


    def __init__(self, parent, root, session, title, sensor, measurement, position, liveMode):
        wx.Panel.__init__(self, parent=parent)
        vboxOuter = wx.BoxSizer(wx.VERTICAL)
        self.devicePanels = []
        self.vboxInner = wx.BoxSizer(wx.VERTICAL)
        self.vboxTitle = wx.BoxSizer(wx.VERTICAL)
        self.midPan = wx.Panel(self)
        self.midPan.SetBackgroundColour('#000237')
        self.isLiveMode = liveMode
        self._parent = parent
        self.boldfont = wx.Font(6, wx.SWISS, wx.NORMAL, wx.BOLD, False, u'Arial')
        self.sensorType = sensor
        self.measurementType = measurement
        self.selectedSession = session
        self.chartTitle = title
        self.root = root
        self._session = session
        self.position = position

        self.optionsBtn = wx.Button(self.midPan, -1, "Options")
        self.optionsBtn.Bind(wx.EVT_BUTTON, self.OnDisplayOptions)
        self.optionsBox = wx.BoxSizer(wx.VERTICAL)
        self.optionsBox.Add(self.optionsBtn, 1, wx.EXPAND)

        # create rows
        self.graphColumn = wx.BoxSizer(wx.VERTICAL)

        self.graphCell_1 = wx.BoxSizer(wx.VERTICAL)
        self.closeCell_1 = wx.Button(self.midPan, -1, "Close")
        self.closeCell_1.Bind(wx.EVT_BUTTON, self.OnCloseCell_1)
        self.graphCell_1.Add(self.closeCell_1, 0, wx.ALIGN_LEFT | wx.LEFT | wx.TOP | wx.BOTTOM, 5)
        self.graphCell_2 = wx.BoxSizer(wx.VERTICAL)
        self.closeCell_2 = wx.Button(self.midPan, -1, "Close")
        self.closeCell_2.Bind(wx.EVT_BUTTON, self.OnCloseCell_2)
        self.graphCell_2.Add(self.closeCell_2, 0, wx.ALIGN_LEFT | wx.LEFT | wx.TOP | wx.BOTTOM, 5)
        self.graphCell_2.Hide(self.closeCell_2)
        self.graphCell_3 = wx.BoxSizer(wx.VERTICAL)
        self.closeCell_3 = wx.Button(self.midPan, -1, "Close")
        self.closeCell_3.Bind(wx.EVT_BUTTON, self.OnCloseCell_3)
        self.graphCell_3.Add(self.closeCell_3, 0, wx.ALIGN_LEFT | wx.LEFT | wx.TOP | wx.BOTTOM, 5)
        self.graphCell_3.Hide(self.closeCell_3)
        self.graphCell_4 = wx.BoxSizer(wx.VERTICAL)
        self.closeCell_4 = wx.Button(self.midPan, -1, "Close")
        self.closeCell_4.Bind(wx.EVT_BUTTON, self.OnCloseCell_4)
        self.graphCell_4.Add(self.closeCell_4, 0, wx.ALIGN_LEFT | wx.LEFT | wx.TOP | wx.BOTTOM, 5)
        self.graphCell_4.Hide(self.closeCell_4)

        self.graphColumn.Add(self.graphCell_1, 1, wx.EXPAND)
        self.graphColumn.Add(self.graphCell_2, 1, wx.EXPAND)
        self.graphColumn.Add(self.graphCell_3, 1, wx.EXPAND)
        self.graphColumn.Add(self.graphCell_4, 1, wx.EXPAND)

        # add first device
        self.devicePanels.append(ModalGraphPanel(self, root, session, title, sensor, measurement, position, liveMode,
                                           isEmbed=True))
        self.graphCell_1.Add(self.devicePanels[0], 1, wx.EXPAND)

        self.vboxInner.Add(self.optionsBox, 0, wx.ALIGN_RIGHT | wx.TOP | wx.RIGHT, 10)
        self.vboxInner.Add(self.graphColumn, 1, wx.EXPAND | wx.ALL, 10)

        self.midPan.SetSizer(self.vboxInner)
        vboxOuter.Add(self.midPan, wx.ID_ANY, wx.EXPAND)
        self.SetSizer(vboxOuter)

    def addChart(self, title, sensor, measurement, position):
        self.devicePanels.append(ModalGraphPanel(self, self.root, self._session, title, sensor, measurement, position, self.isLiveMode,
                                                 isEmbed=True))

        if len(self.devicePanels) == 1:
            self.graphCell_1.Add(self.devicePanels[0], 1, wx.EXPAND)
            self.graphCell_1.Show(self.closeCell_1)
        if len(self.devicePanels) == 2:
            self.graphCell_2.Add(self.devicePanels[1], 1, wx.EXPAND)
            self.graphCell_2.Show(self.closeCell_2)
        elif len(self.devicePanels) == 3:
            self.graphCell_3.Add(self.devicePanels[2], 1, wx.EXPAND)
            self.graphCell_3.Show(self.closeCell_3)
        elif len(self.devicePanels) == 4:
            self.graphCell_4.Add(self.devicePanels[3], 1, wx.EXPAND)
            self.graphCell_4.Show(self.closeCell_4)
        self.Layout()

    def resetCharts(self, index):
        # clear all cells
        for i in range(len(self.devicePanels)):
            if i == 0:
                self.graphCell_1.Hide(self.closeCell_1)
                self.graphCell_1.Hide(self.devicePanels[i])
                self.graphCell_1.Detach(self.devicePanels[i])
            elif i == 1:
                self.graphCell_2.Hide(self.closeCell_2)
                self.graphCell_2.Hide(self.devicePanels[i])
                self.graphCell_2.Detach(self.devicePanels[i])
            elif i == 2:
                self.graphCell_3.Hide(self.closeCell_3)
                self.graphCell_3.Hide(self.devicePanels[i])
                self.graphCell_3.Detach(self.devicePanels[i])
            elif i == 3:
                self.graphCell_4.Hide(self.closeCell_4)
                self.graphCell_4.Hide(self.devicePanels[i])
                self.graphCell_4.Detach(self.devicePanels[i])

        # delete chart at index
        del self.devicePanels[index]

        # add remaining charts
        for i in range(len(self.devicePanels)):
            if i == 0:
                self.graphCell_1.Show(self.closeCell_1)
                self.graphCell_1.Add(self.devicePanels[0], 1, wx.EXPAND)
                self.graphCell_1.Show(self.devicePanels[0])
            elif i == 1:
                self.graphCell_2.Show(self.closeCell_2)
                self.graphCell_2.Add(self.devicePanels[1], 1, wx.EXPAND)
                self.graphCell_2.Show(self.devicePanels[1])
            elif i == 2:
                self.graphCell_3.Show(self.closeCell_3)
                self.graphCell_3.Add(self.devicePanels[2], 1, wx.EXPAND)
                self.graphCell_3.Show(self.devicePanels[2])
            elif i == 3:
                self.graphCell_4.Show(self.closeCell_4)
                self.graphCell_4.Add(self.devicePanels[3], 1, wx.EXPAND)
                self.graphCell_4.Show(self.devicePanels[3])
        self.Layout()

    def OnCloseCell_1(self, event):
        self.resetCharts(0)

    def OnCloseCell_2(self, event):
        self.resetCharts(1)

    def OnCloseCell_3(self, event):
        self.resetCharts(2)

    def OnCloseCell_4(self, event):
        self.resetCharts(3)

    def scaleData(self, startTime, endTime):
        for panel in self.devicePanels:
            panel.scaleData(startTime, endTime)

    def finalizeGraph(self):
        for panel in self.devicePanels:
            panel.finalizeGraph()

    def getStartIndex(self):
        return self.devicePanels[0].getStartIndex()

    def setStartIndex(self, index):
        for panel in self.devicePanels:
            panel.setStartIndex(index)

    def getEndIndex(self):
        return self.devicePanels[0].getEndIndex()

    def setEndIndex(self, index):
        for panel in self.devicePanels:
            panel.setEndIndex(index)

    def getDataScale(self):
        return self.devicePanels[0].getDataScale()

    def getScaleLocked(self):
        return self.devicePanels[0].getScaleLocked()

    def getSessionDuration(self):
        return self.devicePanels[0].getSessionDuration()

    def getTimeUnit(self):
        return self.devicePanels[0].getTimeUnit()

    def getOriginalStartTime(self):
        return self.devicePanels[0].getOriginalStartTime()

    def getOriginalEndTime(self):
        return self.devicePanels[0].getOriginalEndTime()

    def getSessionStartTime(self):
        return self.devicePanels[0].getSessionStartTime()

    def OnDisplayOptions(self, event):
        ModalGraphOptionsFrame(self.selectedSession, self.chartTitle, self.position, parent=self, root=self._parent)
