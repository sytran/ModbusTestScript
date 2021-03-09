"""
    Panel for creating modal graph frames
"""

__version__ = "$Revision: 1.0.0 $"
__author__ = "Wayne Smith"
__status__ = "Internal"
__date__ = "08 January 2021"

from ModalGraphPanel import *
from wx.lib.pubsub import pub as Publisher
import uuid


class ModalGraphFrame(wx.Frame):
    """
    Class used for creating modal graph Frames
    """
    network = None
    devicePanel = None
    root = None
    frameId = None

    def __init__(self, deviceId, network, session, title, sensor, measurement, position, liveMode, parent=None, root=None):
        wx.Frame.__init__(self, parent=parent, title=title, size=(875, 420))
        self.network = None
        self.devicePanel = None
        self.root = None
        self.deviceId = deviceId
        self.frameId = None
        self.devicePanel = ModalGraphPanel(self, root, session, title, sensor, measurement, position, liveMode)
        self._parent = parent
        self.root = root
        self.network = network
        self.frameId = uuid.uuid1()
        self.devicePosition = position
        messageRefreshView = "refreshView" + str(self.network.id) + str(position)
        Publisher.subscribe(self.refreshView, messageRefreshView)
        Publisher.subscribe(self.closeCharts, "closeCharts")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Show()

    def closeCharts(self):
        self._parent.closeAndGoHome()

    def OnClose(self, event):
        self._parent.closeAndGoHome(self.frameId)

    def getReadyForClose(self):
        self.devicePanel = None

    def refreshView(self):
        if self.devicePanel is not None:
            self.devicePanel.refreshGraph()
