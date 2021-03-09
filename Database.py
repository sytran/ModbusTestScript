"""
    Database Classes and setup
"""

__version__ = "$Revision: 1.0.0 $"
__author__ = "Wayne Smith"
__status__ = "Internal"
__date__ = "09 December 2020"

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, PickleType
from Utilities import *

DB_DIR = ROOT_DIR + "\\myron_l_MODBUSConnect.db"
db_path = os.path.join(DB_DIR)
engine = create_engine('sqlite:///' + db_path, echo=True)
Base = declarative_base()


# data base
########################################################################
class Network(Base):
    """"""
    __tablename__ = "network"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    port = Column(Integer)
    baudrate = Column(Integer)
    bytesize = Column(Integer)
    parity = Column(Integer)
    stopbits = Column(Integer)
    timeout = Column(Integer)
    logging = Column(Boolean)

    # ----------------------------------------------------------------------
    def __init__(self, name, port, baudrate, bytesize, parity, stopbits, timeout, logging):
        """Constructor"""
        self.name = name
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.logging = logging

class Device(Base):
    """"""
    __tablename__ = "device"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    address = Column(Integer)
    index = Column(Integer)
    network_id = Column(Integer, ForeignKey('network.id'))

    # ----------------------------------------------------------------------
    def __init__(self, name, address, index, network_id):
        """Constructor"""
        self.name = name
        self.address = address
        self.index = index
        self.network_id = network_id


class LogSession(Base):
    """"""
    __tablename__ = "logsession"
    id = Column(Integer, primary_key=True)
    deviceId = Column(Integer)
    date = Column(String)
    port = Column(Integer)
    baudrate = Column(Integer)
    bytesize = Column(Integer)
    parity = Column(Integer)
    stopbits = Column(Integer)
    timeout = Column(Integer)
    condRes1MeasurementType = Column(String)
    condRes1SolutionType = Column(String)
    condRes1ProbeType = Column(String)
    condRes1MeasurementUnit = Column(String)
    condRes1TemperatureUnit = Column(String)
    condRes2MeasurementType = Column(String)
    condRes2SolutionType = Column(String)
    condRes2ProbeType = Column(String)
    condRes2MeasurementUnit = Column(String)
    condRes2TemperatureUnit = Column(String)
    pHORPMeasurementType = Column(String)
    pHORPProbeType = Column(String)
    pHORPMeasurementUnit = Column(String)
    pHORPTemperatureUnit = Column(String)
    bncMeasurementType = Column(String)
    bncSolutionType = Column(String)
    rtdMeasurementType = Column(String)
    rtdSolutionType = Column(String)
    network_id = Column(Integer, ForeignKey('network.id'))

    # ----------------------------------------------------------------------
    def __init__(self, deviceId, date, port, baudrate, bytesize, parity, stopbits, timeout, condRes1MeasurementType,
                 condRes1SolutionType, condRes1ProbeType, condRes1MeasurementUnit, condRes1TemperatureUnit, condRes2MeasurementType,
                 condRes2SolutionType, condRes2ProbeType, condRes2MeasurementUnit, condRes2TemperatureUnit, pHORPMeasurementType, pHORPProbeType,
                pHORPMeasurementUnit, pHORPTemperatureUnit, bncMeasurementType, bncSolutionType, rtdMeasurementType,
                 rtdSolutionType, network_id):
        """Constructor"""
        self.deviceId = deviceId
        self.date = date
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.condRes1MeasurementType = condRes1MeasurementType
        self.condRes1SolutionType = condRes1SolutionType
        self.condRes1ProbeType = condRes1ProbeType
        self.condRes1MeasurementUnit = condRes1MeasurementUnit
        self.condRes1TemperatureUnit = condRes1TemperatureUnit
        self.condRes2MeasurementType = condRes2MeasurementType
        self.condRes2SolutionType = condRes2SolutionType
        self.condRes2ProbeType = condRes2ProbeType
        self.condRes2MeasurementUnit = condRes2MeasurementUnit
        self.condRes2TemperatureUnit = condRes2TemperatureUnit
        self.pHORPMeasurementType = pHORPMeasurementType
        self.pHORPProbeType = pHORPProbeType
        self.pHORPMeasurementUnit = pHORPMeasurementUnit
        self.pHORPTemperatureUnit = pHORPTemperatureUnit
        self.bncMeasurementType = bncMeasurementType
        self.bncSolutionType = bncSolutionType
        self.rtdMeasurementType = rtdMeasurementType
        self.rtdSolutionType = rtdSolutionType
        self.network_id = network_id


class LogSessionMeasurement(Base):
    """"""
    __tablename__ = "logsessionmeasurement"

    id = Column(Integer, primary_key=True)
    start = Column(String)
    end = Column(String)
    logList = Column(PickleType)
    session_id = Column(Integer, ForeignKey('logsession.id'))

    # ----------------------------------------------------------------------
    def __init__(self, start, end, logList, session_id):
        """Constructor"""
        self.start = start
        self.end = end
        self.logList = logList
        self.session_id = session_id
