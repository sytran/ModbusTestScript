"""
    Panel for graphing modal data
"""

__version__ = "$Revision: 1.0.0 $"
__author__ = "Wayne Smith"
__status__ = "Internal"
__date__ = "08 January 2021"

from random import randrange, uniform
import wx.lib.plot as plot

from ModalGraphOptionsFrame import *


class BucketTracker:
    def __init__(self):
        self.time = None
        self.values = []


class ModalGraphPanel(wx.Panel):
    boldfont = None
    logSessionMeasurementsForDevice = []
    bucketArray = []
    rawLogData = []
    contiguousDataArray = []
    sessionStartTime = 0
    sessionEndTime = 0
    sessionDuration = 0
    position = 0
    sensorType = ""
    measurementType = ""
    selectedSession = None
    chartTitle = ""
    root = None
    refreshTime = None
    shouldRefreshGraph = False
    shouldGenerateMockData = False
    mockDataDuration = 1440
    startIndex = 0
    endIndex = DATA_RANGE
    dataScale = DEFAULT_GRAPH_TIMESCALE
    scaleLocked = False
    originalStartTime = None
    originalEndTime = None
    timeUnit = SECONDS
    estimatedSampleRate = 0

    def __init__(self, parent, root, session, title, sensor, measurement, position, liveMode, isEmbed=False):
        wx.Panel.__init__(self, parent=parent)
        self.SetBackgroundColour('#000237')
        vboxOuter = wx.BoxSizer(wx.VERTICAL)
        self.vboxInner = wx.BoxSizer(wx.VERTICAL)
        self.vboxTitle = wx.BoxSizer(wx.VERTICAL)
        self.midPan = wx.Panel(self)
        self.midPan.SetBackgroundColour('#0512D2')
        self.isLiveMode = liveMode
        self._parent = parent
        self.boldfont = wx.Font(6, wx.SWISS, wx.NORMAL, wx.BOLD, False, u'Arial')
        self.sensorType = sensor
        self.measurementType = measurement
        self.selectedSession = session
        self.chartTitle = title
        self.root = root
        self.position = position

        # put some text with a larger bold font on it
        self.title = wx.StaticText(self.midPan, label="")
        font = self.title.GetFont()
        font.PointSize += 8
        font = font.Bold()
        self.title.SetFont(font)
        self.title.SetForegroundColour('#FFFFFF')
        self.vboxTitle.Add(self.title, 1, wx.ALIGN_CENTER)

        self.graphBox = wx.BoxSizer(wx.VERTICAL)
        self.plotter = plot.PlotCanvas(self.midPan)
        self.plotter.SetEnableZoom(False)
        self.plotter.SetEnableAntiAliasing(True)
        self.plotter.SetBackgroundColour('#0512D2')
        self.plotter.SetForegroundColour('#FFFFFF')
        self.graphBox.Add(self.plotter, 1, wx.EXPAND)

        self.optionsBtn = wx.Button(self.midPan, -1, "Options")
        self.optionsBtn.Bind(wx.EVT_BUTTON, self.OnDisplayOptions)

        self.vboxInner.Add(self.optionsBtn, 0, wx.ALIGN_RIGHT | wx.TOP | wx.RIGHT, 5)
        self.vboxInner.Add(self.graphBox, 1, wx.EXPAND | wx.ALL, 5)
        self.vboxInner.Add(self.vboxTitle, 1, wx.ALIGN_CENTER | wx.TOP, 20)
        self.vboxInner.Hide(self.vboxTitle)

        self.midPan.SetSizer(self.vboxInner)
        if isEmbed:
            self.vboxInner.Hide(self.optionsBtn)
            vboxOuter.Add(self.midPan, wx.ID_ANY, wx.EXPAND)
            self.midPan.SetBackgroundColour('#000237')
        else:
            vboxOuter.Add(self.midPan, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)
        self.SetSizer(vboxOuter)
        self.loadView()

    def OnDisplayOptions(self, event):
        ModalGraphOptionsFrame(self.selectedSession, self.chartTitle, self.position, parent=self, root=self._parent)

    def loadView(self):
        self.bucketArray = []
        self.rawLogData = []
        if self.isLiveMode:
            print("is liveMode")
            self.vboxInner.Hide(self.optionsBtn)
        else:
            self.setUpSessionData(None)
        self.Layout()

    def setStartIndex(self, index):
        self.startIndex = index

    def setEndIndex(self, index):
        self.endIndex = index

    def getStartIndex(self):
        return self.startIndex

    def getEndIndex(self):
        return self.endIndex

    def getDataScale(self):
        return self.dataScale

    def getScaleLocked(self):
        return self.scaleLocked

    def getSessionDuration(self):
        return self.sessionDuration

    def getTimeUnit(self):
        return self.timeUnit

    def getOriginalStartTime(self):
        return self.originalStartTime

    def getOriginalEndTime(self):
        return self.originalEndTime

    def getSessionStartTime(self):
        return self.sessionStartTime

    def refreshGraph(self):
        if self.isLiveMode:
            for network in self.root.activeNetworks:
                if network.network.id == self._parent.network.id:
                    liveList = network.liveDataStreams[self._parent.deviceId]
                    if len(liveList) >= 2:
                        self.setUpSessionData(liveList)
                    break

    def generateMockData(self, minutes):
        mockData = []
        sensorTypes = ["COND/RES1", "COND/RES2"]
        measurementTypes = ["primary", "temp"]
        currentTime = datetime.datetime.now()
        seconds = minutes * 60
        # number of periods
        for _ in range(seconds):
            # equal chance for "COND/RES1", "COND/RES2", or no reading
            sensorRange = randrange(3)
            if sensorRange < 2:
                sensorType = sensorTypes[sensorRange]
                measurementType = measurementTypes[randrange(2)]
                if measurementType == "primary":
                    value = uniform(250, 300)
                else:
                    value = uniform(2, 14)

                mockData.append({"sensorType": sensorType, "measurementType": measurementType,
                                 "time": currentTime.strftime("%Y-%m-%d %H:%M:%S"), "value": value})
            currentTime += datetime.timedelta(seconds=1)
        return mockData

    def setUpSessionData(self, liveList):
        if self.isLiveMode:
            for data in liveList:
                if data["sensorType"] == self.sensorType and data["measurementType"] == self.measurementType:
                    recentLiveMeasurement = data["time"]
                    if self.rawLogData:
                        lastLiveMeasurement = self.rawLogData[len(self.rawLogData) - 1]["time"]
                    else:
                        lastLiveMeasurement = recentLiveMeasurement
                    if not self.rawLogData or datetime.datetime.strptime(recentLiveMeasurement,
                                                                         TIME_FMT) > datetime.datetime.strptime(
                        lastLiveMeasurement,
                        TIME_FMT):
                        self.rawLogData.append(data)
                        if self.refreshTime is None:
                            self.refreshTime = recentLiveMeasurement
                        else:
                            updateTime = datetime.datetime.strptime(recentLiveMeasurement,
                                                                    TIME_FMT) - datetime.datetime.strptime(
                                self.refreshTime, TIME_FMT)
                            if updateTime.total_seconds() > GRAPH_REFRESH_INTERVAL:
                                self.shouldRefreshGraph = True
                                self.refreshTime = recentLiveMeasurement

                        logSize = len(self.rawLogData) - 1
                        for _ in range(logSize):
                            firstLiveMeasurement = self.rawLogData[0]["time"]
                            liveTime = datetime.datetime.strptime(recentLiveMeasurement,
                                                                  TIME_FMT) - datetime.datetime.strptime(
                                firstLiveMeasurement, TIME_FMT)
                            if liveTime.total_seconds() > RECORD_INTERVAL:
                                self.rawLogData.pop(0)
                            else:
                                break
        else:
            if not self.shouldGenerateMockData:
                self.logSessionMeasurementsForDevice = self.root.GetLogSessionMeasurementsForSessionId(
                    self.selectedSession.id)
                # get raw data for desired sensor(s)
                for logEntry in self.logSessionMeasurementsForDevice:
                    for value in logEntry.logList:
                        if value["sensorType"] == self.sensorType and value["measurementType"] == self.measurementType:
                            self.rawLogData.append(value)
            else:
                mockData = self.generateMockData(self.mockDataDuration)
                for value in mockData:
                    if value["sensorType"] == self.sensorType and value["measurementType"] == self.measurementType:
                        self.rawLogData.append(value)

        if len(self.rawLogData) > 1:
            self.vboxInner.Hide(self.vboxTitle)
            self.vboxInner.Show(self.graphBox)
            self.originalStartTime = self.rawLogData[0]["time"]
            self.originalEndTime = self.rawLogData[len(self.rawLogData) - 1]["time"]
            self.scaleData(self.originalStartTime, self.originalEndTime)
        else:
            self.title.SetLabel("No Data for " + self.sensorType + " " + self.measurementType)
            self.vboxInner.Show(self.vboxTitle)
            self.vboxInner.Hide(self.graphBox)

    def scaleData(self, startTime, endTime):
        if not self.isLiveMode or (self.isLiveMode and self.shouldRefreshGraph):
            self.shouldRefreshGraph = False
            if len(self.rawLogData) > 1:
                # calculate session start time and duration based on data set
                self.sessionStartTime = datetime.datetime.strptime(startTime, TIME_FMT)
                self.sessionEndTime = datetime.datetime.strptime(endTime, TIME_FMT)
                time = self.sessionEndTime - self.sessionStartTime
                self.sessionDuration = time.total_seconds()
                if self.sessionDuration > DATA_RANGE:
                    self.dataScale = self.scale()
                    self.sessionDuration = self.dataScale * DATA_RANGE
                    self.scaleLocked = False
                else:
                    self.timeUnit = SECONDS
                    self.dataScale = DEFAULT_GRAPH_TIMESCALE
                    self.scaleLocked = True
                    self.startIndex = 0
                    self.endIndex = int(self.sessionDuration)
                self.updateSensorDataAndGraph()
            else:
                self.title.SetLabel("No Data for " + self.sensorType + " " + self.measurementType)
                self.vboxInner.Show(self.vboxTitle)
                self.vboxInner.Hide(self.graphBox)

    def scale(self):
        if self.sessionDuration < 3600:
            # < one hours
            self.timeUnit = MINUTES
            minutes = int(self.sessionDuration / 60)
            remainder = self.sessionDuration % 60
            if remainder == 0:
                return minutes / (DATA_RANGE * 1.0)
            else:
                return (minutes + remainder / 60) / DATA_RANGE
        elif self.sessionDuration < 86400:
            # < one day
            self.timeUnit = HOURS
            hours = int(self.sessionDuration / 3600)
            remainder = self.sessionDuration % 3600
            if remainder == 0:
                return hours / (DATA_RANGE * 1.0)
            else:
                return (hours + remainder / 3600) / DATA_RANGE
        else:
            self.timeUnit = DAYS
            days = int(self.sessionDuration / 86400)
            remainder = self.sessionDuration % 86400
            if self.sessionDuration % 86400 == 0:
                return days / (DATA_RANGE * 1.0)
            else:
                return (days + remainder / 86400) / DATA_RANGE

    def scaleTime(self, time):
        if self.timeUnit == SECONDS:
            return time.total_seconds()
        elif self.timeUnit == MINUTES:
            return time.total_seconds() / 60
        elif self.timeUnit == HOURS:
            return time.total_seconds() / 3600
        else:
            return time.total_seconds() / 86400

    def updateSensorDataAndGraph(self):
        maxNumberOfBuckets = DATA_RANGE

        # generate buckets
        self.bucketArray = []
        for _ in range(maxNumberOfBuckets):
            self.bucketArray.append(BucketTracker())

        previousTime = None
        valueSum = 0.0
        valueCount = 0

        # populate buckets
        for entry in self.rawLogData:
            entryTime = datetime.datetime.strptime(entry["time"], TIME_FMT)
            if self.sessionStartTime <= entryTime <= self.sessionEndTime:
                if previousTime is None:
                    previousTime = entryTime
                else:
                    if entryTime > previousTime:
                        diff = entryTime - previousTime
                        valueSum += diff.total_seconds()
                        valueCount += 1
                    previousTime = entryTime

                time = entryTime - self.sessionStartTime
                # buckets should be inclusive of high value
                index = int(self.scaleTime(time) / self.dataScale)
                if time.total_seconds() % self.dataScale == 0 and index > 0:
                    index -= 1
                if index < len(self.bucketArray):
                    self.bucketArray[index].time = time.total_seconds()
                    self.bucketArray[index].values.append(entry["value"])

        # estimate sample rate for given sample range
        numberOfDevices = 0
        for network in self.root.activeNetworks:
            numberOfDevices += len(network.deviceResponders)

        if self.isLiveMode:
            self.estimatedSampleRate = numberOfDevices
        else:
            self.estimatedSampleRate = valueSum / valueCount

        # generate contiguous array of sensor data based on buckets
        self.contiguousDataArray = []
        currentValue = (0, 0)
        for tracker in self.bucketArray:
            if tracker.time is None:
                self.contiguousDataArray.append(currentValue)
            else:
                newValue = 0
                for value in tracker.values:
                    newValue += value
                # get mean
                newValue = newValue / len(tracker.values)
                self.contiguousDataArray.append((tracker.time, int(newValue * 10000) / 10000.0))
                currentValue = self.contiguousDataArray[-1]
        self.finalizeGraph()

    def finalizeGraph(self):
        # create tuple array, get graph min and max values
        dataByRange = []

        # update startIndex if needed (set cannot start with a zero)
        for i in range(self.startIndex, self.endIndex):
            if self.contiguousDataArray[i][1] != 0:
                break
            else:
                self.startIndex += 1

        for i in range(self.startIndex, self.endIndex):
            dataByRange.append(self.contiguousDataArray[i])

        updatedData = []
        currentTime = None
        # if duration between first values is very large assume larger sample rate
        updateZoom = False
        for data in dataByRange:
            if currentTime is None or (data[0] - currentTime) >= self.estimatedSampleRate:
                currentTime = data[0]
                updatedData.append(data[1])
            else:
                updateZoom = True
        dataByRange = updatedData

        if dataByRange:
            currentScale = self.dataScale
            if updateZoom:
                if self.timeUnit == MINUTES:
                    currentScale = self.estimatedSampleRate / 60.0
                    if self.estimatedSampleRate > 10:
                        self.scaleLocked = True
                if self.timeUnit == SECONDS:
                    currentScale = self.estimatedSampleRate
            graphTime = currentScale
            tupleData = []
            xMin = currentScale
            xMax = currentScale * len(dataByRange)
            yMin = dataByRange[0]
            yMax = dataByRange[0]
            for data in dataByRange:
                if data > yMax:
                    yMax = data
                if data < yMin:
                    yMin = data
                tupleData.append((graphTime, data))
                graphTime += currentScale

            # graph data
            line = plot.PolyLine(tupleData, colour='red', width=3)
            marker = plot.PolyMarker(tupleData, colour='#000237', marker='circle', size=1)
            unitLabel = ""

            if self.sensorType == "COND/RES1":
                if self.measurementType == "primary":
                    unitLabel = self.selectedSession.condRes1MeasurementUnit
                elif self.measurementType == "temp":
                    unitLabel = self.selectedSession.condRes1TemperatureUnit

            elif self.sensorType == "COND/RES2":
                if self.measurementType == "primary":
                    unitLabel = self.selectedSession.condRes2MeasurementUnit
                elif self.measurementType == "temp":
                    unitLabel = self.selectedSession.condRes2TemperatureUnit

            elif self.sensorType == "PH/ORP":
                if self.measurementType == "primary":
                    unitLabel = self.selectedSession.pHORPMeasurementUnit
                elif self.measurementType == "temp":
                    unitLabel = self.selectedSession.pHORPTemperatureUnit

            graphTitle = self.chartTitle + " " + self.sensorType + " " + unitLabel + ": "
            if self.isLiveMode:
                graphTitle += "LIVE"
            else:
                graphTitle += self.selectedSession.date

            unit = "(sec)"
            if self.timeUnit == MINUTES:
                unit = "(min)"
            elif self.timeUnit == HOURS:
                unit = "(hr)"
            elif self.timeUnit == DAYS:
                unit = "(day)"

            gc = plot.PlotGraphics([line, marker], graphTitle, "Session Duration " + unit, unitLabel)
            self.plotter.Draw(gc, xAxis=(xMin, xMax), yAxis=(yMin, yMax))
            self.Layout()
