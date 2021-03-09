#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    MODBUS Connect Root File
"""

__version__ = "$Revision: 1.0.0 $"
__author__ = "Wayne Smith"
__status__ = "Internal"
__date__ = "9 December 2020"

from ModbusConnect import *


def main():
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = ModbusConnect(None, title='Modbus Connect')
    frm.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
