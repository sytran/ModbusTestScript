"""
    Panel for creating modal graph frames
"""

__version__ = "$Revision: 1.0.0 $"
__author__ = "Wayne Smith"
__status__ = "Internal"
__date__ = "22 January 2021"


from ModalGraphEmbedPanel import *
from wx.lib.pubsub import pub as Publisher
import uuid


class ModalGraphEmbedFrame(wx.Frame):
    """
    Class used for creating embedded modal graph embed Frames
    """

    devicePanel = None
    root = None
    frameId = None

    def __init__(self, session, title, sensor, measurement, position, liveMode, parent=None, root=None):
        wx.Frame.__init__(self, parent=parent, title=title, size=(875, 840))
        self.devicePanel = ModalGraphEmbedPanel(self, root, session, title, sensor, measurement, position, liveMode)
        self._parent = parent
        self.root = root
        self._session = session
        self.frameId = uuid.uuid1()
        self.devicePosition = position
        Publisher.subscribe(self.closeCharts, "closeCharts")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Show()

    def closeCharts(self):
        self._parent.closeAndGoHome()

    def addChart(self, title, sensor, measurement, position):
        self.devicePanel.addChart(title, sensor, measurement, position)

    def OnClose(self, event):
        self._parent.closeAndGoHome(self.frameId)

    def getReadyForClose(self):
        self.devicePanel = None

