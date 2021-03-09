"""
    Application Utilities
"""

__version__ = "$Revision: 1.0.0 $"
__author__ = "Wayne Smith"
__status__ = "Internal"
__date__ = "09 December 2020"

import os

# relay/alarm registers
MODBUS_FUNCTION_RELAYS_ALARMS_REGISTERS = 2
RELAY_1_STATE = 1
RELAY_2_STATE = 2
RELAY_3_STATE = 3
ALARM_1_STATE = 4
ALARM_2_STATE = 5
FLOW_SWITCH_STATE = 6

RELAY_ALARM_REGISTER_START = 0

# config registers
MODBUS_FUNCTION_CONFIG_REGISTERS = 3
CONFIG_COND_RES1 = 0
CONFIG_COND_RES1_TEMP = 2
CONFIG_COND_RES2 = 4
CONFIG_COND_RES2_TEMP = 6
CONFIG_PH_ORP = 8
CONFIG_PH_ORP_TEMP = 10
CONFIG_BNC = 12
CONFIG_RTD = 14
CONFIG_FLOW_PULSE = 16
CONFIG_FLOW_ACC_VOLUME = 18
CONFIG_CURRENT_IN = 20
CONFIG_CURRENT_OUT = 22
CONFIG_VOLTAGE_OUT = 24
CONFIG_REJECTION_RATIO = 26
CONFIG_ORP_2 = 28

# data registers
MODBUS_FUNCTION_DATA_REGISTERS = 4
DATA_COND_RES1 = 0
DATA_COND_RES1_TEMP = 2
DATA_COND_RES2 = 4
DATA_COND_RES2_TEMP = 6
DATA_PH_ORP = 8
DATA_PH_ORP_TEMP = 10
DATA_BNC = 12
DATA_RTD = 14
DATA_FLOW_PULSE = 16
DATA_FLOW_ACC_VOLUME = 18
DATA_CURRENT_IN = 20
DATA_CURRENT_OUT = 22
DATA_VOLTAGE_OUT = 24
DATA_REJECTION_RATIO = 26
DATA_ORP_2 = 28

DATA_VALUES_COUNT = 15
DATA_REGISTER_START = 0

READ_INTERVAL = 0.40
DATA_STORAGE_INTERVAL = 0.20
UI_REFRESH_INTERVAL = 0.60
RECORD_INTERVAL = 30
GRAPH_REFRESH_INTERVAL = 1
DEFAULT_GRAPH_TIMESCALE = 1
DATA_RANGE = 250

SECONDS = 0
MINUTES = 1
HOURS = 2
DAYS = 3


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

TIME_FMT = '%Y-%m-%d %H:%M:%S'


# uncomment for saving as exe via py2exe
# size = len(ROOT_DIR)
# ROOT_DIR = ROOT_DIR[:size - 9]

def reverse(s):
    return s[::-1]


def sensorTypeDescription(id):
    if id == "0":
        return "None"
    elif id == "1":
        return "COND/RES1"
    elif id == "2":
        return "RTD1"
    elif id == "3":
        return "COND/RES2"
    elif id == "4":
        return "RTD2"
    elif id == "5":
        return "pH/ORP"
    elif id == "6":
        return "RTD3"
    elif id == "7":
        return "mV IN"
    elif id == "8":
        return "RTD"
    elif id == "9":
        return "4-20mA IN"
    elif id == "10":
        return "PULSE IN"
    elif id == "11":
        return "%Rejection"
    else:
        return ""


def measurementTypeDescription(id):
    if id == "0":
        return "None"
    elif id == "1":
        return "Conductivity"
    elif id == "2":
        return "Resistivity"
    elif id == "3":
        return "TDS"
    elif id == "4":
        return "Salinity"
    elif id == "5":
        return "ORP"
    elif id == "6":
        return "pH"
    elif id == "7":
        return "pH (TC Off)"
    elif id == "8":
        return "mV"
    elif id == "9":
        return "420mA Current"
    elif id == "10":
        return "420mA Measurement"
    elif id == "11":
        return "Temperature"
    elif id == "12":
        return "Flow"
    elif id == "13":
        return "Volume"
    elif id == "14":
        return "Pulse"
    else:
        return ""


def probeTypeDescription(id, isCOND=False):
    if isCOND:
        if id == "0":
            return "None"
        elif id == "1":
            return "CS910"
        elif id == "2":
            return "CS951"
        elif id == "3":
            return "CS952"
        elif id == "4":
            return "CS952"
        else:
            return ""
    else:
        if id == "0":
            return "None"
        elif id == "1":
            return "MLC pH"
        elif id == "2":
            return "MLC ORP"
        elif id == "3":
            return "Generic"
        else:
            return ""


def solutionTypeDescription(id):
    if id == "0":
        return "None"
    elif id == "1":
        return "KCl"
    elif id == "2":
        return "NaCl"
    elif id == "3":
        return "442"
    elif id == "4":
        return "User"
    else:
        return ""


def measurementUnitDescription(id):
    if id == "0":
        return "None"
    elif id == "1":
        return "uS"
    elif id == "2":
        return "mS"
    elif id == "3":
        return "ppm"
    elif id == "4":
        return "ppt"
    elif id == "5":
        return "mV"
    elif id == "6":
        return "V"
    elif id == "7":
        return "C"
    elif id == "8":
        return "F"
    elif id == "9":
        return "Ohm"
    elif id == "10":
        return "kohm"
    elif id == "11":
        return "Mohm"
    elif id == "12":
        return "mA"
    elif id == "13":
        return "Hz"
    elif id == "14":
        return "kHz"
    elif id == "15":
        return "Gallon/Second"
    elif id == "16":
        return "Gallon/Minute"
    elif id == "17":
        return "Gallon/Hour"
    elif id == "18":
        return "Liter/Second"
    elif id == "19":
        return "Liter/Minute"
    elif id == "20":
        return "Liter/Hour"
    elif id == "21":
        return "Gallon"
    elif id == "22":
        return "Liter"
    elif id == "23":
        return "%"
    elif id == "24":
        return "psi"
    elif id == "25":
        return "NTU"
    elif id == "26":
        return "Second"
    elif id == "27":
        return "Minute"
    elif id == "28":
        return "Hour"
    elif id == "29":
        return "Pulse Per Gallon"
    elif id == "30":
        return "Pulse Per Liter"
    else:
        return ""

