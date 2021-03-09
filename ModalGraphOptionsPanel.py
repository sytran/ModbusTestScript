"""
    Panel for model graph options
"""

__version__ = "$Revision: 1.0.0 $"
__author__ = "Wayne Smith"
__status__ = "Internal"
__date__ = "12 January 2021"

import wx
import datetime
from Utilities import *


class ModalGraphOptionsPanel(wx.Panel):

    previousZoom = []

    def __init__(self, parent, subparent, root, session, title, position):
        wx.Panel.__init__(self, parent=parent)
        self.SetBackgroundColour('#000237')
        vboxOuter = wx.BoxSizer(wx.VERTICAL)
        self.vboxInner = wx.BoxSizer(wx.VERTICAL)
        self.vboxTitle = wx.BoxSizer(wx.VERTICAL)
        self.midPan = wx.Panel(self)
        self.midPan.SetBackgroundColour('#0512D2')

        self._parent = parent
        self.boldfont = wx.Font(6, wx.SWISS, wx.NORMAL, wx.BOLD, False, u'Arial')
        self.selectedSession = session
        self.chartTitle = title
        self.root = root
        self.subparent = subparent
        self.position = position

        # put some text with a larger bold font on it
        self.title = wx.StaticText(self.midPan, label=title + " Options")
        font = self.title.GetFont()
        font.PointSize += 8
        font = font.Bold()
        self.title.SetFont(font)
        self.title.SetForegroundColour('#FFFFFF')
        self.vboxTitle.Add(self.title, 1, wx.ALIGN_CENTER)

        self.optionsBox = wx.StaticBox(self.midPan, 1, 'Options')
        self.optionsBox.SetForegroundColour('#FFFFFF')
        self.optionsBoxSizer = wx.StaticBoxSizer(self.optionsBox, wx.VERTICAL)

        self.fromStaticBox = wx.StaticBox(self.midPan, 1, 'From')
        self.fromStaticBox.SetForegroundColour('#FFFFFF')
        self.fromStaticBoxSizer = wx.StaticBoxSizer(self.fromStaticBox, wx.VERTICAL)
        self.fromBoxSizer = wx.BoxSizer(wx.VERTICAL)

        self.rangeLabelFrom = wx.StaticText(self.midPan, -1, "1")
        rangeLabelFromFont = self.rangeLabelFrom.GetFont()
        rangeLabelFromFont.PointSize += 2
        rangeLabelFromFont = rangeLabelFromFont.Bold()
        self.rangeLabelFrom.SetFont(rangeLabelFromFont)
        self.rangeLabelFrom.SetForegroundColour('#FFFFFF')

        self.sldFrom = wx.Slider(self.midPan, value=0, minValue=0, maxValue=DATA_RANGE-10,
                             style=wx.SL_HORIZONTAL)
        self.sldFrom.Bind(wx.EVT_SLIDER, self.OnSliderScrollFrom)

        self.fromBoxSizer.Add(self.rangeLabelFrom, 0, wx.ALIGN_CENTER | wx.TOP, 5)
        self.fromBoxSizer.Add(self.sldFrom, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        self.fromStaticBoxSizer.Add(self.fromBoxSizer, 1, wx.EXPAND | wx.ALL, 5)

        self.toStaticBox = wx.StaticBox(self.midPan, 1, 'To')
        self.toStaticBox.SetForegroundColour('#FFFFFF')
        self.toStaticBoxSizer = wx.StaticBoxSizer(self.toStaticBox, wx.VERTICAL)
        self.toBoxSizer = wx.BoxSizer(wx.VERTICAL)

        self.rangeLabelTo = wx.StaticText(self.midPan, -1, "1")
        rangeLabelToFont = self.rangeLabelTo.GetFont()
        rangeLabelToFont.PointSize += 2
        rangeLabelToFont = rangeLabelToFont.Bold()
        self.rangeLabelTo.SetFont(rangeLabelToFont)
        self.rangeLabelTo.SetForegroundColour('#FFFFFF')

        self.sldTo = wx.Slider(self.midPan, value=DATA_RANGE, minValue=10, maxValue=DATA_RANGE,
                              style=wx.SL_HORIZONTAL)
        self.sldTo.Bind(wx.EVT_SLIDER, self.OnSliderScrollTo)

        self.toBoxSizer.Add(self.rangeLabelTo, 0, wx.ALIGN_CENTER | wx.TOP, 5)
        self.toBoxSizer.Add(self.sldTo, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        self.toStaticBoxSizer.Add(self.toBoxSizer, 1, wx.EXPAND | wx.ALL, 5)

        self.zoomInDataBtn = wx.Button(self.midPan, -1, "Zoom In")
        self.zoomInDataBtn.Bind(wx.EVT_BUTTON, self.zoomInData)

        self.zoomOutDataBtn = wx.Button(self.midPan, -1, "Zoom Out")
        self.zoomOutDataBtn.Bind(wx.EVT_BUTTON, self.zoomOutData)

        self.resetDataBtn = wx.Button(self.midPan, -1, "Reset")
        self.resetDataBtn.Bind(wx.EVT_BUTTON, self.resetData)

        self.controlsBox = wx.BoxSizer(wx.HORIZONTAL)
        self.controlsBox.Add(self.zoomInDataBtn, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        self.controlsBox.Add(self.zoomOutDataBtn, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        self.controlsBox.Add(self.resetDataBtn, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        self.optionsBoxSizer.Add(self.fromStaticBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
        self.optionsBoxSizer.Add(self.toStaticBoxSizer, 1, wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5)
        self.optionsBoxSizer.Add(self.controlsBox, 0, wx.ALIGN_CENTER)

        self.vboxInner.Add(self.vboxTitle, 0, wx.ALIGN_CENTER | wx.TOP, 10)
        self.vboxInner.Add(self.optionsBoxSizer, 1, wx.EXPAND | wx.ALL, 20)

        self.midPan.SetSizer(self.vboxInner)
        vboxOuter.Add(self.midPan, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)
        self.SetSizer(vboxOuter)

    def optionsSetUp(self):
        self.rangeLabelFrom.SetLabel(self.subparent.getOriginalStartTime())
        self.rangeLabelTo.SetLabel(self.subparent.getOriginalEndTime())
        self.previousZoom = []
        self.previousZoom.append((self.rangeLabelFrom.GetLabel(), self.rangeLabelTo.GetLabel()))
        self.zoomOutDataBtn.Disable()
        self.resetDataBtn.Disable()
        self.zoomInDataBtn.Disable()

    def zoom(self, start, end):
        self.sldFrom.SetValue(0)
        self.sldTo.SetValue(DATA_RANGE)
        self.subparent.setStartIndex(0)
        self.subparent.setEndIndex(DATA_RANGE)
        self.subparent.scaleData(start, end)
        self.zoomInDataBtn.Disable()

    def zoomInData(self, event):
        self.zoom(self.rangeLabelFrom.GetLabel(), self.rangeLabelTo.GetLabel())
        self.previousZoom.append((self.rangeLabelFrom.GetLabel(), self.rangeLabelTo.GetLabel()))
        if self.subparent.getScaleLocked():
            self.zoomInDataBtn.Disable()
        self.zoomOutDataBtn.Enable()
        self.resetDataBtn.Enable()

    def zoomOutData(self, event):
        #discard current zoom
        if len(self.previousZoom) > 1:
            self.previousZoom.pop(-1)
        if self.previousZoom:
            previousZoom = self.previousZoom[-1]
            self.rangeLabelFrom.SetLabel(previousZoom[0])
            self.rangeLabelTo.SetLabel(previousZoom[1])
            self.zoom(previousZoom[0], previousZoom[1])
        else:
            self.resetData(None)

    def resetData(self, event):
        self.rangeLabelFrom.SetLabel(self.subparent.getOriginalStartTime())
        self.rangeLabelTo.SetLabel(self.subparent.getOriginalEndTime())
        self.zoom(self.subparent.getOriginalStartTime(), self.subparent.getOriginalEndTime())
        self.zoomInDataBtn.Disable()
        self.zoomOutDataBtn.Disable()
        self.resetDataBtn.Disable()

    def enableDisableZoomIn(self):
        if self.subparent.getStartIndex() == 0 and self.subparent.getEndIndex() == DATA_RANGE:
            self.zoomInDataBtn.Disable()
            self.resetDataBtn.Disable()
        else:
            self.zoomInDataBtn.Enable()
            self.resetDataBtn.Enable()

    def OnSliderScrollFrom(self, event):
        if not self.subparent.getScaleLocked():
            self.enableDisableZoomIn()
        obj = event.GetEventObject()
        value = obj.GetValue()
        if self.subparent.getTimeUnit() == SECONDS:
            self.subparent.setStartIndex(int((value / (DATA_RANGE * 1.0)) * self.subparent.getSessionDuration()))
        else:
            self.subparent.setStartIndex(value)
        time = self.subparent.getStartIndex() * self.subparent.getDataScale()
        if self.subparent.getTimeUnit() == SECONDS:
            time = self.subparent.getSessionStartTime() + datetime.timedelta(seconds=time)
        elif self.subparent.getTimeUnit() == MINUTES:
            time = self.subparent.getSessionStartTime() + datetime.timedelta(minutes=time)
        elif self.subparent.getTimeUnit() == HOURS:
            time = self.subparent.getSessionStartTime() + datetime.timedelta(hours=time)
        elif self.subparent.getTimeUnit() == DAYS:
            time = self.subparent.getSessionStartTime() + datetime.timedelta(days=time)
        self.rangeLabelFrom.SetLabel(time.strftime("%Y-%m-%d %H:%M:%S"))
        if self.subparent.getTimeUnit() == SECONDS:
            sliderBuffer = self.subparent.getEndIndex() - int((10 / (DATA_RANGE * 1.0)) * self.subparent.getSessionDuration())
        else:
            sliderBuffer = self.subparent.getEndIndex() - 10
        if self.subparent.getStartIndex() > sliderBuffer:
            if self.subparent.getTimeUnit() == SECONDS:
                self.subparent.setEndIndex(self.subparent.getEndIndex() + int((10 / (DATA_RANGE * 1.0)) * self.subparent.getSessionDuration()))
                self.sldTo.SetValue(int((self.subparent.getEndIndex() * DATA_RANGE) / self.subparent.getSessionDuration()))
            else:
                self.subparent.setEndIndex(self.subparent.getEndIndex() + 10)
                self.sldTo.SetValue(self.subparent.getEndIndex())
            time = self.subparent.getStartIndex() * self.subparent.getDataScale()
            if self.subparent.getTimeUnit() == SECONDS:
                time = self.subparent.getSessionStartTime() + datetime.timedelta(seconds=time)
            elif self.subparent.getTimeUnit() == MINUTES:
                time = self.subparent.getSessionStartTime() + datetime.timedelta(minutes=time)
            elif self.subparent.getTimeUnit() == HOURS:
                time = self.subparent.getSessionStartTime() + datetime.timedelta(hours=time)
            elif self.subparent.getTimeUnit() == DAYS:
                time = self.subparent.getSessionStartTime() + datetime.timedelta(days=time)
            self.rangeLabelTo.SetLabel(time.strftime("%Y-%m-%d %H:%M:%S"))
        self.subparent.finalizeGraph()

    def OnSliderScrollTo(self, event):
        if not self.subparent.getScaleLocked():
            self.enableDisableZoomIn()
        obj = event.GetEventObject()
        value = obj.GetValue()
        if self.subparent.getTimeUnit() == SECONDS:
            self.subparent.setEndIndex(int((value / (DATA_RANGE * 1.0)) * self.subparent.getSessionDuration()))
        else:
            self.subparent.setEndIndex(value)
        time = self.subparent.getEndIndex() * self.subparent.getDataScale()
        if self.subparent.getTimeUnit() == SECONDS:
            time = self.subparent.getSessionStartTime() + datetime.timedelta(seconds=time)
        elif self.subparent.getTimeUnit() == MINUTES:
            time = self.subparent.getSessionStartTime() + datetime.timedelta(minutes=time)
        elif self.subparent.getTimeUnit() == HOURS:
            time = self.subparent.getSessionStartTime() + datetime.timedelta(hours=time)
        elif self.subparent.getTimeUnit() == DAYS:
            time = self.subparent.getSessionStartTime() + datetime.timedelta(days=time)
        self.rangeLabelTo.SetLabel(time.strftime("%Y-%m-%d %H:%M:%S"))
        if self.subparent.getTimeUnit() == SECONDS:
            sliderBuffer = self.subparent.getStartIndex() + int((10 / (DATA_RANGE * 1.0)) * self.subparent.getSessionDuration())
        else:
            sliderBuffer = self.subparent.getStartIndex() + 10
        if self.subparent.getEndIndex() < sliderBuffer:
            if self.subparent.getTimeUnit() == SECONDS:
                self.subparent.setStartIndex(self.subparent.getStartIndex() - int((10 / (DATA_RANGE * 1.0)) * self.subparent.getSessionDuration))
                self.sldFrom.SetValue(int((self.subparent.getStartIndex() * DATA_RANGE) / self.subparent.getSessionDuration()))
            else:
                self.subparent.setStartIndex(self.subparent.getStartIndex() - 10)
                self.sldFrom.SetValue(self.subparent.getStartIndex())
            time = self.subparent.getStartIndex() * self.subparent.getDataScale()
            if self.subparent.getTimeUnit() == SECONDS:
                time = self.subparent.getSessionStartTime() + datetime.timedelta(seconds=time)
            elif self.subparent.getTimeUnit() == MINUTES:
                time = self.subparent.getSessionStartTime() + datetime.timedelta(minutes=time)
            elif self.subparent.getTimeUnit() == HOURS:
                time = self.subparent.getSessionStartTime() + datetime.timedelta(hours=time)
            elif self.subparent.getTimeUnit() == DAYS:
                time = self.subparent.getSessionStartTime() + datetime.timedelta(days=time)
            self.rangeLabelFrom.SetLabel(time.strftime("%Y-%m-%d %H:%M:%S"))
        self.subparent.finalizeGraph()
