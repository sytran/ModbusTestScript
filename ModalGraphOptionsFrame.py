"""
    Frame for model graph options
"""

__version__ = "$Revision: 1.0.0 $"
__author__ = "Wayne Smith"
__status__ = "Internal"
__date__ = "12 January 2021"

from ModalGraphOptionsPanel import *


class ModalGraphOptionsFrame(wx.Frame):
    """
    Class used for creating modal graph Frames
    """

    def __init__(self, session, title, position, parent=None, root=None):
        wx.Frame.__init__(self, parent=parent, title=title, size=(875, 420))
        self.settingsPanel = ModalGraphOptionsPanel(self, parent, root, session, title, position)
        self.settingsPanel.optionsSetUp()
        self._parent = parent
        self.root = root
        self.Show()
