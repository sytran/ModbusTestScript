"""
    Panel for device data
"""

__version__ = "$Revision: 1.0.0 $"
__author__ = "Wayne Smith"
__status__ = "Internal"
__date__ = "09 December 2020"

import wx
import wx.grid as gridlib


class DevicePanel(wx.Panel):
    _frameParent = None
    root = None
    condRes1Measurement = None
    condRes1Temp = None
    condRes2Measurement = None
    condRes2Temp = None
    pHORPMeasurement = None
    pHORPTemp = None
    bncMeasurement = None
    rtdMeasurement = None
    dataList = []
    deviceId = None
    logSessionId = None

    def __init__(self, parent, root, id, frameParent, thisTitle):
        wx.Panel.__init__(self, parent=parent)
        self.SetBackgroundColour('#000237')
        vboxOuter = wx.BoxSizer(wx.VERTICAL)
        vboxInner = wx.BoxSizer(wx.VERTICAL)
        vboxTitle = wx.BoxSizer(wx.VERTICAL)
        self._parent = parent
        self._frameParent = frameParent
        self.root = root
        self.deviceId = id
        self.configDictionary = []
        self.dataArray = []
        self.bitArray = []
        midPan = wx.Panel(self)
        midPan.SetBackgroundColour('#0512D2')

        # put some text with a larger bold font on it
        title = wx.StaticText(midPan, label=thisTitle)
        font = title.GetFont()
        font.PointSize += 5
        font = font.Bold()
        title.SetFont(font)
        title.SetForegroundColour('#FFFFFF')
        vboxTitle.Add(title, 1, wx.ALIGN_CENTER)

        self.myGrid = gridlib.Grid(midPan)
        self.myGrid.CreateGrid(13, 6)
        font = self.myGrid.GetCellFont(0, 0)
        font = font.Bold()

        self.myGrid.SetDefaultColSize(120, True)
        self.myGrid.SetCellValue(0, 0, "COND_RES1")
        self.myGrid.SetCellFont(0, 0, font)
        self.myGrid.SetReadOnly(0, 0, True)

        self.myGrid.SetCellValue(0, 2, "COND_RES1_TEMP")
        self.myGrid.SetCellFont(0, 2, font)
        self.myGrid.SetReadOnly(0, 2, True)

        self.myGrid.SetCellValue(0, 4, "COND_RES2")
        self.myGrid.SetCellFont(0, 4, font)
        self.myGrid.SetReadOnly(0, 4, True)

        self.myGrid.SetCellValue(2, 0, "COND_RES2_TEMP")
        self.myGrid.SetCellFont(2, 0, font)
        self.myGrid.SetReadOnly(2, 0, True)

        self.myGrid.SetCellValue(2, 2, "PH_ORP")
        self.myGrid.SetCellFont(2, 2, font)
        self.myGrid.SetReadOnly(2, 2, True)

        self.myGrid.SetCellValue(2, 4, "PH_ORP_TEMP")
        self.myGrid.SetCellFont(2, 4, font)
        self.myGrid.SetReadOnly(2, 4, True)

        self.myGrid.SetCellValue(4, 0, "ORP_2")
        self.myGrid.SetCellFont(4, 0, font)
        self.myGrid.SetReadOnly(4, 0, True)

        self.myGrid.SetCellValue(4, 2, "BNC")
        self.myGrid.SetCellFont(4, 2, font)
        self.myGrid.SetReadOnly(4, 2, True)

        self.myGrid.SetCellValue(4, 4, "RTD")
        self.myGrid.SetCellFont(4, 4, font)
        self.myGrid.SetReadOnly(4, 4, True)

        self.myGrid.SetCellValue(6, 0, "FLOW_PULSE")
        self.myGrid.SetCellFont(6, 0, font)
        self.myGrid.SetReadOnly(6, 0, True)

        self.myGrid.SetCellValue(6, 2, "FLOW_ACC_VOLUME")
        self.myGrid.SetCellFont(6, 2, font)
        self.myGrid.SetReadOnly(6, 2, True)

        self.myGrid.SetCellValue(6, 4, "CURRENT_IN")
        self.myGrid.SetCellFont(6, 4, font)
        self.myGrid.SetReadOnly(6, 4, True)

        self.myGrid.SetCellValue(8, 0, "CURRENT_OUT")
        self.myGrid.SetCellFont(8, 0, font)
        self.myGrid.SetReadOnly(8, 0, True)

        self.myGrid.SetCellValue(8, 2, "VOLTAGE_OUT")
        self.myGrid.SetCellFont(8, 2, font)
        self.myGrid.SetReadOnly(8, 2, True)

        self.myGrid.SetCellValue(8, 4, "Relay 1")
        self.myGrid.SetCellFont(8, 4, font)
        self.myGrid.SetReadOnly(8, 4, True)

        self.myGrid.SetCellValue(10, 0, "Relay 2")
        self.myGrid.SetCellFont(10, 0, font)
        self.myGrid.SetReadOnly(10, 0, True)

        self.myGrid.SetCellValue(10, 2, "Relay 3")
        self.myGrid.SetCellFont(10, 2, font)
        self.myGrid.SetReadOnly(10, 2, True)

        self.myGrid.SetCellValue(10, 4, "Alarm 1")
        self.myGrid.SetCellFont(10, 4, font)
        self.myGrid.SetReadOnly(10, 4, True)

        self.myGrid.SetCellValue(12, 0, "Alarm 2")
        self.myGrid.SetCellFont(12, 0, font)
        self.myGrid.SetReadOnly(12, 0, True)

        self.myGrid.SetCellValue(12, 2, "Flow Switch")
        self.myGrid.SetCellFont(12, 2, font)
        self.myGrid.SetReadOnly(12, 2, True)

        gridSizer = wx.BoxSizer(wx.VERTICAL)
        gridSizer.Add(self.myGrid, 1, wx.EXPAND)
        vboxInner.Add(vboxTitle, 0, wx.ALIGN_CENTER | wx.TOP, 10)
        vboxInner.Add(gridSizer, 1, wx.EXPAND)
        midPan.SetSizer(vboxInner)
        vboxOuter.Add(midPan, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)
        self.SetSizer(vboxOuter)

    def refreshView(self):
        for network in self.root.activeNetworks:
            if network.network.id == self._parent.network.id:
                if self._parent.deviceId in network.configDataStreams:
                    self.refreshConfig_labels(network.configDataStreams[self._parent.deviceId])
                    self.refreshData_labels(network.dataDataStreams[self._parent.deviceId],
                                            network.configDataStreams[self._parent.deviceId])
                    self.refreshRelaysAlarms_labels(network.bitDataStreams[self._parent.deviceId])
                    break

    def refreshConfig_labels(self, configDictionary):
        if self._frameParent is not None and configDictionary is not None:
            # COND/RES1
            measurementType = configDictionary['COND/RES1']['MeasurementType']
            solutionType = configDictionary['COND/RES1']['SolutionType']
            probeType = configDictionary['COND/RES1']['ProbeType']
            self.setDATA_COND_RES1_MEASUREMENT_TYPE_label(measurementType)
            self.setDATA_COND_RES1_MEASUREMENT_DETAILS_label(solutionType + ", " + probeType)

            # COND/RES2
            measurementType = configDictionary['COND/RES2']['MeasurementType']
            solutionType = configDictionary['COND/RES2']['SolutionType']
            probeType = configDictionary['COND/RES2']['ProbeType']
            self.setDATA_COND_RES2_MEASUREMENT_TYPE_label(measurementType)
            self.setDATA_COND_RES2_MEASUREMENT_DETAILS_label(solutionType + ", " + probeType)

            # PH/ORP
            measurementType = configDictionary['PH/ORP']['MeasurementType']
            probeType = configDictionary['PH/ORP']['ProbeType']
            self.setDATA_PH_ORP_MEASUREMENT_TYPE_label(measurementType)
            self.setDATA_PH_ORP_MEASUREMENT_DETAILS_label(probeType)

            # BNC
            measurementType = configDictionary['BNC']['MeasurementType']
            probeType = configDictionary['BNC']['ProbeType']
            self.setDATA_BNC_MEASUREMENT_TYPE_label(measurementType)
            self.setDATA_BNC_MEASUREMENT_DETAILS_label(probeType)

            # RTD
            measurementType = configDictionary['RTD']['MeasurementType']
            probeType = configDictionary['RTD']['ProbeType']
            self.setDATA_RTD_MEASUREMENT_TYPE_label(measurementType)
            self.setDATA_RTD_MEASUREMENT_DETAILS_label(probeType)

    def refreshData_labels(self, dataArray, configDictionary):
        if self._frameParent is not None and dataArray is not None and configDictionary is not None:

            dataCOND_RES1 = dataArray[0]
            if dataCOND_RES1 is not None and float(dataCOND_RES1):
                unit = configDictionary['COND/RES1']['MeasurementUnit']
                self.setDATA_COND_RES1_label(format(float(dataCOND_RES1), '.4f') + " " + unit)
            else:
                self.setDATA_COND_RES1_label(str(dataCOND_RES1))

            dataCOND_RES1_TEMP = dataArray[1]
            if dataCOND_RES1_TEMP is not None and float(dataCOND_RES1_TEMP):
                unit = configDictionary['COND/RES1']['TemperatureUnit']
                self.setDATA_COND_RES1_TEMP_label(format(float(dataCOND_RES1_TEMP), '.4f') + " " + unit)
            else:
                self.setDATA_COND_RES1_TEMP_label(str(dataCOND_RES1_TEMP))

            dataCOND_RES2 = dataArray[2]
            if dataCOND_RES2 is not None and float(dataCOND_RES2):
                unit = configDictionary['COND/RES2']['MeasurementUnit']
                self.setDATA_COND_RES2_label(format(float(dataCOND_RES2), '.4f') + " " + unit)
            else:
                self.setDATA_COND_RES2_label(str(dataCOND_RES2))

            dataCOND_RES2_TEMP = dataArray[3]
            if dataCOND_RES2_TEMP is not None and float(dataCOND_RES2_TEMP):
                unit = configDictionary['COND/RES2']['TemperatureUnit']
                self.setDATA_COND_RES2_TEMP_label(format(float(dataCOND_RES2_TEMP), '.4f') + " " + unit)
            else:
                self.setDATA_COND_RES2_TEMP_label(str(dataCOND_RES2_TEMP))

            dataPH_ORP = dataArray[4]
            if dataPH_ORP is not None and float(dataPH_ORP):
                unit = configDictionary['PH/ORP']['MeasurementUnit']
                self.setDATA_PH_ORP_label(format(float(dataPH_ORP), '.4f') + " " + unit)
            else:
                self.setDATA_PH_ORP_label(str(dataPH_ORP))

            dataPH_ORP_TEMP = dataArray[5]
            if dataPH_ORP_TEMP is not None and float(dataPH_ORP_TEMP):
                unit = configDictionary['PH/ORP']['TemperatureUnit']
                self.setDATA_PH_ORP_TEMP_label(format(float(dataPH_ORP_TEMP), '.4f') + " " + unit)
            else:
                self.setDATA_PH_ORP_TEMP_label(str(dataPH_ORP_TEMP))

            dataORP_2 = dataArray[6]
            if dataORP_2 is not None and float(dataORP_2):
                self.setDATA_ORP_2_label(format(float(dataORP_2), '.4f'))
            else:
                self.setDATA_ORP_2_label(str(dataORP_2))

            dataBNC = dataArray[7]
            if dataBNC is not None and float(dataBNC):
                self.setDATA_BNC_label(format(float(dataBNC), '.4f'))
            else:
                self.setDATA_BNC_label(str(dataBNC))

            dataRTD = dataArray[8]
            if dataRTD is not None and float(dataRTD):
                self.setDATA_RTD_label(format(float(dataRTD), '.4f'))
            else:
                self.setDATA_RTD_label(str(dataRTD))

            dataFLOW_PULSE = dataArray[9]
            if dataFLOW_PULSE is not None and float(dataFLOW_PULSE):
                self.setDATA_FLOW_PULSE_label(format(float(dataFLOW_PULSE), '.4f'))
            else:
                self.setDATA_FLOW_PULSE_label(str(dataFLOW_PULSE))

            dataFLOW_ACC_VOLUME = dataArray[10]
            if dataFLOW_ACC_VOLUME is not None and float(dataFLOW_ACC_VOLUME):
                self.setDATA_FLOW_ACC_VOLUME_label(format(float(dataFLOW_ACC_VOLUME), '.4f'))
            else:
                self.setDATA_FLOW_ACC_VOLUME_label(str(dataFLOW_ACC_VOLUME))

            dataCURRENT_IN = dataArray[11]
            if dataCURRENT_IN is not None and float(dataCURRENT_IN):
                self.setDATA_CURRENT_IN_label(format(float(dataCURRENT_IN), '.4f'))
            else:
                self.setDATA_CURRENT_IN_label(str(dataCURRENT_IN))

            dataCURRENT_OUT = dataArray[12]
            if dataCURRENT_OUT is not None and float(dataCURRENT_OUT):
                self.setDATA_CURRENT_OUT_label(format(float(dataCURRENT_OUT), '.4f'))
            else:
                self.setDATA_CURRENT_OUT_label(str(dataCURRENT_OUT))

            dataVOLTAGE_OUT = dataArray[13]
            if dataVOLTAGE_OUT is not None and float(dataVOLTAGE_OUT):
                self.setDATA_VOLTAGE_OUT_label(format(float(dataVOLTAGE_OUT), '.4f'))
            else:
                self.setDATA_VOLTAGE_OUT_label(str(dataVOLTAGE_OUT))

    def refreshRelaysAlarms_labels(self, bitArray):
        if self._frameParent is not None and self.bitArray is not None:
            relay1 = bitArray[0]
            if relay1:
                self.setRelay1_label("On")
            else:
                self.setRelay1_label("Off")

            relay2 = bitArray[1]
            if relay2:
                self.setRelay2_label("On")
            else:
                self.setRelay2_label("Off")

            relay3 = bitArray[2]
            if relay3:
                self.setRelay3_label("On")
            else:
                self.setRelay3_label("Off")

            alarm1 = bitArray[3]
            if alarm1:
                self.setAlarm1_label("On")
            else:
                self.setAlarm1_label("Off")

            alarm2 = bitArray[4]
            if alarm2:
                self.setAlarm2_label("On")
            else:
                self.setAlarm2_label("Off")

            flowSwitch = bitArray[5]
            if flowSwitch:
                self.setFlowSwitch_label("On")
            else:
                self.setFlowSwitch_label("Off")

    def setDATA_COND_RES1_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(0, 1, value)

    def setDATA_COND_RES1_MEASUREMENT_TYPE_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(1, 0, value)

    def setDATA_COND_RES1_MEASUREMENT_DETAILS_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(1, 1, value)

    def setDATA_COND_RES1_TEMP_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(0, 3, value)

    def setDATA_COND_RES2_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(0, 5, value)

    def setDATA_COND_RES2_MEASUREMENT_TYPE_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(1, 4, value)

    def setDATA_COND_RES2_MEASUREMENT_DETAILS_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(1, 5, value)

    def setDATA_COND_RES2_TEMP_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(2, 1, value)

    def setDATA_PH_ORP_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(2, 3, value)

    def setDATA_PH_ORP_MEASUREMENT_TYPE_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(3, 2, value)

    def setDATA_PH_ORP_MEASUREMENT_DETAILS_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(3, 3, value)

    def setDATA_PH_ORP_TEMP_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(2, 5, value)

    def setDATA_ORP_2_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(4, 1, value)

    def setDATA_BNC_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(4, 3, value)

    def setDATA_BNC_MEASUREMENT_TYPE_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(5, 2, value)

    def setDATA_BNC_MEASUREMENT_DETAILS_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(5, 3, value)

    def setDATA_RTD_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(4, 5, value)

    def setDATA_RTD_MEASUREMENT_TYPE_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(5, 4, value)

    def setDATA_RTD_MEASUREMENT_DETAILS_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(5, 5, value)

    def setDATA_FLOW_PULSE_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(6, 1, value)

    def setDATA_FLOW_ACC_VOLUME_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(6, 3, value)

    def setDATA_CURRENT_IN_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(6, 5, value)

    def setDATA_CURRENT_OUT_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(8, 1, value)

    def setDATA_VOLTAGE_OUT_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(8, 3, value)

    def setRelay1_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(8, 5, value)

    def setRelay2_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(10, 1, value)

    def setRelay3_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(10, 3, value)

    def setAlarm1_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(10, 5, value)

    def setAlarm2_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(12, 1, value)

    def setFlowSwitch_label(self, value):
        if self.myGrid is not None:
            self.myGrid.SetCellValue(12, 3, value)

    def GoToMainMenu(self, event):
        self._parent.OnMainMenu()
