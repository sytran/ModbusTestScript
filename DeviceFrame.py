"""
    Panel for creating device frames
"""

__version__ = "$Revision: 1.0.0 $"
__author__ = "Wayne Smith"
__status__ = "Internal"
__date__ = "09 December 2020"

from DevicePanel import *
from wx.lib.pubsub import pub as Publisher


class DeviceFrame(wx.Frame):
    """
    Class used for creating Device Frames
    """
    network = None
    devicePanel = None
    devicePosition = None
    root = None
    _parent = None
    deviceId = None

    def __init__(self, network, id, title, parent=None, root=None, position=None):
        wx.Frame.__init__(self, parent=parent, title=title, size=(875, 420))
        self.devicePosition = position
        self.network = network
        self.root = root
        self.deviceId = id
        self.devicePanel = DevicePanel(self, root, id, parent, title)
        self._parent = parent
        messageRefreshView = "refreshView" + str(self.network.id) + str(position)
        Publisher.subscribe(self.refreshView, messageRefreshView)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Show()

    def refreshView(self):
        if self.devicePanel is not None:
            self.devicePanel.refreshView()

    def OnClose(self, event):
        self._parent.closeAndGoHome()

    def getReadyForClose(self):
        self.devicePanel = None
