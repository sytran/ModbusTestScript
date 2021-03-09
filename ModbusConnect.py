#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Root application class
"""

__version__ = "$Revision: 1.0.0 $"
__author__ = "Wayne Smith"
__status__ = "Internal"
__date__ = "9 December 2020"

from functools import partial
from MainPanel import *
from CreateNetworkPanel import *
from EditNetworkPanel import *
from DisplayNetworkPanel import *
from DisplayModalGraphPanel import *
from CSVImportPanel import *
from NetworkStatusPanel import *
from Database import *
from sqlalchemy.orm import sessionmaker
import datetime


class ModbusConnect(wx.Frame):
    networks = []
    currentSelectedNetwork = None
    currentInstruments = []
    editNetworkMenu = None
    displayNetworkMenu = None
    displayGraphMenu = None
    liveList = []
    panelFrames = []
    activeNetworks = []

    def __init__(self, parent, title):
        super(ModbusConnect, self).__init__(parent, title=title,
                                            size=(1920, 1080))
        self.Centre()
        self.InitUI()
        self.Maximize(False)

        # create database if needed
        self.createDataBaseIfNeeded()

        # create a menu bar
        self.makeMenuBar()

    def InitUI(self):

        self.mainPanel = MainPanel(self)
        self.createNetworkPanel = CreateNetworkPanel(self)
        self.networkStatusPanel = NetworkStatusPanel(self)
        self.editNetworkPanel = EditNetworkPanel(self)
        self.displayNetworkPanel = DisplayNetworkPanel(self)
        self.csvImportPanel = CSVImportPanel(self)
        self.modalDisplayGraphPanel = DisplayModalGraphPanel(self)
        self.createNetworkPanel.Hide()
        self.networkStatusPanel.Hide()
        self.editNetworkPanel.Hide()
        self.displayNetworkPanel.Hide()
        self.modalDisplayGraphPanel.Hide()
        self.csvImportPanel.Hide()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.mainPanel, 1, wx.EXPAND)
        self.sizer.Add(self.createNetworkPanel, 1, wx.EXPAND)
        self.sizer.Add(self.networkStatusPanel, 1, wx.EXPAND)
        self.sizer.Add(self.editNetworkPanel, 1, wx.EXPAND)
        self.sizer.Add(self.displayNetworkPanel, 1, wx.EXPAND)
        self.sizer.Add(self.modalDisplayGraphPanel, 1, wx.EXPAND)
        self.sizer.Add(self.csvImportPanel, 1, wx.EXPAND)
        self.SetSizer(self.sizer)

    def createDataBaseIfNeeded(self):
        dbFound = False
        for filename in os.listdir(ROOT_DIR):
            if filename.find(".db") != -1:
                dbFound = True
                break
        if dbFound:
            print "db already created"
        else:
            print "creating db"
            Base.metadata.create_all(engine)

    def makeMenuBar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        fileMenu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        homeItem = fileMenu.Append(-1, "&Home...\tCtrl-H",
                                   "Help string shown in status bar for this menu item")
        newNetworkItem = fileMenu.Append(-1, "&New Network")
        networkStatus = fileMenu.Append(-1, "&Network Status")
        fileMenu.AppendSeparator()
        exitItem = fileMenu.Append(wx.ID_EXIT)

        self.editNetworkMenu = wx.Menu()
        self.displayNetworkMenu = wx.Menu()
        self.displayGraphMenu = wx.Menu()

        Session = sessionmaker(bind=engine)
        session = Session()
        self.networks = session.query(Network).order_by(Network.name)
        self.updateCurrentNetworks()

        # utilities menu
        utilitiesMenu = wx.Menu()
        csvImportItem = utilitiesMenu.Append(-1, "&Import CSV")

        # help menu
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        self.menuBar = wx.MenuBar()
        self.menuBar.Append(fileMenu, "&File")
        self.menuBar.Append(self.editNetworkMenu, "&Edit")
        self.menuBar.Append(self.displayNetworkMenu, "&Display")
        self.menuBar.Append(self.displayGraphMenu, "&Graph")
        self.menuBar.Append(utilitiesMenu, "&Utilities")
        self.menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(self.menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnHome, homeItem)
        self.Bind(wx.EVT_MENU, self.OnNewNetwork, newNetworkItem)
        self.Bind(wx.EVT_MENU, self.OnNetworkStatus, networkStatus)
        self.Bind(wx.EVT_MENU, self.OnExit, exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)
        self.Bind(wx.EVT_MENU, self.OnCSVImport, csvImportItem)

    def updateCurrentNetworks(self):
        # clear current menu items
        rangeValue = self.editNetworkMenu.GetMenuItemCount()
        for _ in range(rangeValue):
            self.editNetworkMenu.DestroyItem(self.editNetworkMenu.FindItemByPosition(0))
            self.displayNetworkMenu.DestroyItem(self.displayNetworkMenu.FindItemByPosition(0))
            self.displayGraphMenu.DestroyItem(self.displayGraphMenu.FindItemByPosition(0))

        # bind network names to menu
        count = 0
        for network in self.networks:
            self.Bind(wx.EVT_MENU, partial(self.OnEditNetwork, count),
                      self.editNetworkMenu.Append(-1, "&" + network.name))
            self.Bind(wx.EVT_MENU, partial(self.OnDisplayNetwork, count),
                      self.displayNetworkMenu.Append(-1, "&" + network.name))
            self.Bind(wx.EVT_MENU, partial(self.OnDisplayGraph, count),
                      self.displayGraphMenu.Append(-1, "&" + network.name))
            count = count + 1
        self.Layout()

    def showPanelForValue(self, value):
        if value == "MainPanel":
            self.mainPanel.Show()
        else:
            self.mainPanel.Hide()
        if value == "CreateNetworkPanel":
            self.createNetworkPanel.loadView(self.currentSelectedNetwork)
            self.createNetworkPanel.Show()
        else:
            self.createNetworkPanel.Hide()
        if value == "EditNetworkDetailsPanel":
            self.createNetworkPanel.loadView(self.currentSelectedNetwork, isEditMode=True)
            self.createNetworkPanel.Show()
        elif value != "CreateNetworkPanel":
            self.createNetworkPanel.Hide()
        if value == "NetworkStatusPanel":
            self.networkStatusPanel.loadView()
            self.networkStatusPanel.Show()
        else:
            self.networkStatusPanel.Hide()
        if value == "EditNetworkPanel":
            self.editNetworkPanel.loadView(self.currentSelectedNetwork)
            self.editNetworkPanel.Show()
        else:
            self.editNetworkPanel.Hide()
        if value == "DisplayNetworkPanel":
            self.displayNetworkPanel.loadView(self.currentSelectedNetwork)
            self.displayNetworkPanel.Show()
        else:
            self.displayNetworkPanel.Hide()
        if value == "DisplayGraphPanel":
            self.modalDisplayGraphPanel.loadView(self.currentSelectedNetwork)
            self.modalDisplayGraphPanel.Show()
        else:
            self.modalDisplayGraphPanel.Hide()
        if value == "CSVImportPanel":
            self.csvImportPanel.loadView()
            self.csvImportPanel.Show()
        else:
            self.csvImportPanel.Hide()
        self.Layout()

    def OnHome(self, event):
        """Home Selection"""

        if not self.mainPanel.IsShown():
            if self.displayNetworkPanel.IsShown():
                self.displayNetworkPanel.ToolBarExitToMainMenu()
            if self.editNetworkPanel.IsShown():
                self.displayNetworkPanel.ToolBarExitToMainMenu()
            if self.modalDisplayGraphPanel.IsShown():
                self.modalDisplayGraphPanel.ToolBarExitToMainMenu()
            self.OnMainMenu()

    def updateDevicesForSelectedNetwork(self, network):
        Session = sessionmaker(bind=engine)
        session = Session()
        devicesForSelectedNetwork = session.query(Device).filter(
            Device.network_id == network.id).order_by(Device.index.asc())
        return devicesForSelectedNetwork

    def getDevicesForSelectedNetwork(self, id):
        Session = sessionmaker(bind=engine)
        session = Session()
        return session.query(Device).filter(
            Device.network_id == id).order_by(Device.index.asc())

    def updateNetworkDetails(self, network, name, port, baudrate, bytesize, parity, stopbits, timeout, logging):
        updatedNetwork = None
        Session = sessionmaker(bind=engine)
        session = Session()
        session.query(Network).filter(Network.id == network.id).update(
            {"name": name, "port": port, "baudrate": baudrate, "bytesize": bytesize,
             "parity": parity, "stopbits": stopbits, "timeout": timeout, "logging": logging})

        session.commit()
        # update network info
        self.networks = session.query(Network).order_by(Network.name)
        for i in range(self.networks.count()):
            if self.networks[i].id == network.id:
                updatedNetwork = self.networks[i]
                break

        self.currentSelectedNetwork = updatedNetwork

        return updatedNetwork

    def CreateNewSession(self, network, deviceId, condRes1MeasurementType, condRes1SolutionType, condRes1ProbeType,
                         condRes1MeasurementUnit, condRes1TemperatureUnit, condRes2MeasurementType,
                         condRes2SolutionType, condRes2ProbeType, condRes2MeasurementUnit, condRes2TemperatureUnit,
                         pHORPMeasurementType, pHORPProbeType, pHORPMeasurementUnit, pHORPTemperatureUnit,
                         bncMeasurementType, bncSolutionType,
                         rtdMeasurementType, rtdSolutionType):
        currentDateTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(LogSession(deviceId, currentDateTime, network.port, network.baudrate,
                               network.bytesize, network.parity,
                               network.stopbits, network.timeout, condRes1MeasurementType,
                               condRes1SolutionType, condRes1ProbeType, condRes1MeasurementUnit,
                               condRes1TemperatureUnit, condRes2MeasurementType, condRes2SolutionType,
                               condRes2ProbeType, condRes2MeasurementUnit, condRes2TemperatureUnit,
                               pHORPMeasurementType, pHORPProbeType, pHORPMeasurementUnit, pHORPTemperatureUnit,
                               bncMeasurementType, bncSolutionType, rtdMeasurementType, rtdSolutionType,
                               network.id))
        session.commit()

    def GetLogSessionsForDeviceId(self, deviceId):
        Session = sessionmaker(bind=engine)
        session = Session()
        logSessions = session.query(LogSession).filter(LogSession.deviceId == deviceId).order_by(LogSession.id.desc())
        return logSessions

    def GetLogSessionMeasurementsForSessionId(self, sessionId):
        Session = sessionmaker(bind=engine)
        session = Session()
        logSessions = session.query(LogSessionMeasurement).filter(LogSessionMeasurement.session_id == sessionId).order_by(LogSessionMeasurement.start.asc())
        return logSessions

    def GetNextLogSessionId(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        nextSessionId = 1
        nextSession = session.query(LogSession).order_by(LogSession.id.desc()).first()
        if nextSession is not None:
            nextSessionId = nextSession.id
            nextSessionId += 1

        return nextSessionId

    def CreateLogRecord(self, start, end, logList, session_id):
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(LogSessionMeasurement(start, end, logList, session_id))
        session.commit()

    def CreateNetwork(self, name, port, baudrate, bytesize, parity, stopbits, timeout, logging):
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(Network(name, port, baudrate, bytesize, parity, stopbits, timeout, logging))
        session.commit()
        self.updateCurrentNetworks()

    def CreateDevice(self, name, address, index, network_id):
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(Device(name, address, index, network_id))
        session.commit()

    def DeleteDevice(self, network, index):
        Session = sessionmaker(bind=engine)
        session = Session()
        session.query(Device).filter(Device.network_id == network.id).filter(Device.index == index).delete()
        session.commit()

    def UpdateDeviceIndexMatch(self, network, index):
        Session = sessionmaker(bind=engine)
        session = Session()
        oldIndex = index + 1
        session.query(Device).filter(Device.network_id == network.id).filter(Device.index == oldIndex).update({"index": index})
        session.commit()

    def UpdateDeviceIndex(self, id, newIndex):
        Session = sessionmaker(bind=engine)
        session = Session()
        session.query(Device).filter(Device.id == id).update({"index": newIndex})
        session.commit()

    def UpdateDeviceNameAndAddress(self, network, index, name, address):
        Session = sessionmaker(bind=engine)
        session = Session()
        session.query(Device).filter(Device.network_id == network.id).filter(Device.index == index).update(
            {"name": name, "address": address})
        session.commit()

    def OnNewNetwork(self, event):
        self.showPanelForValue("CreateNetworkPanel")

    def OnNetworkStatus(self, event):
        self.showPanelForValue("NetworkStatusPanel")

    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)

    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("This is the MODBUS Connect application",
                      "About MODBUS Connect",
                      wx.OK | wx.ICON_INFORMATION)

    def OnEditNetwork(self, number, event):
        self.currentSelectedNetwork = self.networks[number]
        self.showPanelForValue("EditNetworkPanel")

    def OnDisplayNetwork(self, number, event):
        self.currentSelectedNetwork = self.networks[number]
        self.showPanelForValue("DisplayNetworkPanel")

    def OnDisplayGraph(self, number, event):
        self.currentSelectedNetwork = self.networks[number]
        self.showPanelForValue("DisplayGraphPanel")

    def OnCSVImport(self, name):
        self.showPanelForValue("CSVImportPanel")

    def OnMainMenu(self):
        # update menu bar
        self.showPanelForValue("MainPanel")
