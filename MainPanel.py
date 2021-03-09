"""
    Root application panel view
"""

__version__ = "$Revision: 1.0.0 $"
__author__ = "Wayne Smith"
__status__ = "Internal"
__date__ = "09 December 2020"

import wx


class MainPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)

        self.SetBackgroundColour('#000237')
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox2 = wx.BoxSizer(wx.VERTICAL)

        midPan = wx.Panel(self)
        midPan.SetBackgroundColour('#0512D2')

        # put some text with a larger bold font on it
        title = wx.StaticText(midPan, label="Modbus Connect")
        titleFont = title.GetFont()
        titleFont.PointSize += 20
        titleFont = titleFont.Bold()
        title.SetFont(titleFont)
        title.SetForegroundColour('#FFFFFF')

        # put some text with a larger bold font on it
        content = wx.StaticText(midPan, label="This program edits, displays and logs data from MODBUS RS485 networks.",
                                style=wx.ALIGN_CENTER)
        contentFont = content.GetFont()
        contentFont.PointSize += 2
        contentFont = contentFont.Bold()
        content.SetFont(contentFont)
        content.SetForegroundColour('#FFFFFF')

        selectText = wx.StaticText(midPan, label="SELECT the desired MENU OPTION", style=wx.ALIGN_CENTER)
        selectFont = selectText.GetFont()
        selectFont.PointSize += 2
        selectFont = selectFont.Bold()
        selectText.SetFont(selectFont)
        selectText.SetForegroundColour('#FFFFFF')

        titleBox = wx.BoxSizer(wx.VERTICAL)
        titleBox.Add(title, 0, wx.ALIGN_CENTER | wx.TOP, 20)

        contentBox = wx.BoxSizer(wx.VERTICAL)
        contentBox.Add(content, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        contentBox.Add(selectText, 0, wx.ALIGN_CENTER | wx.ALL, 20)

        vbox2.Add(titleBox, 1, wx.ALIGN_CENTER)
        vbox2.Add(contentBox, 1, wx.ALIGN_CENTER)
        midPan.SetSizer(vbox2)
        vbox.Add(midPan, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)
        self.SetSizer(vbox)
