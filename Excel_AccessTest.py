#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    MODBUS Connect Root File
"""

__version__ = "$Revision: 1.0.0 $"
__author__ = "Sy Tran"
__status__ = "Internal"
__date__ = "1 March 2021"

import os
import time
import xlrd
import xlwt
import xlsxwriter
#import openpyxl
import minimalmodbus
import NetworkStatusPanel
import random
import Utilities



# READ_DISCRETE_INPUT = 2  # read 900 Alarms and Relays status
# READ_CONFIG_REGISTER = 3  # 900S configuration = READ_HOLDING_REGISTER
# READ_STATUS_REGISTER = 4  # 900s Status = READ_INPUT_REGISTER
#
# # Define 900 Series Modbus registers address
SERIES_900_REGISTER_SIZE = 30
#
# COND1_STATUS = 0
# COND1_TEMPERATURE = 2
# COND1_STATUS = 4
# COND1_TEMPERATURE = 6
# MLC_pH_STATUS = 8
# MLC_pH_TEMPERATURE = 10
# EXT_pH_ORP_STATUS = 12
# EXT_pH_RTD_TEMPERATURE = 14
# FLOW_FREQUENCY = 16
# FLOW_VOLUME = 18
# IN_420_mA = 20
# OUT_420_mA = 22
# OUT_REC_VOLT = 24
# REJECTION_RATIO = 26
# ORP2_STATUS = 28
RELAYS_ALARMS_STATUS = 30


class Modbus_Driver:
    def __init__(self, port, baudrate, device_number):
        # Set up instrument
        self.instrument = minimalmodbus.Instrument(port, device_number, mode="rtu")

        # Make the settings explicit
        self.instrument.serial.baudrate = baudrate  # Baud
        self.instrument.serial.bytesize = 8
        self.instrument.serial.parity = minimalmodbus.serial.PARITY_EVEN
        self.instrument.serial.stopbits = 1
        self.instrument.serial.timeout = 1  # seconds

        # Good practice
        self.instrument.close_port_after_each_call = True
        self.instrument.clear_buffers_before_each_transaction = True

        self.file_in = 'testSetup/MCL900_Modbus_Registers.xls'
        self.wb_in = xlrd.open_workbook(self.file_in)
        #self.ws_in = self.wb_in.sheet_by_name(self.device_id)
        #self.file_out = 'testSetup/MCL900_Modbus_TestResult.xls'
        #self.wb_out = xlwt.Workbook()
        self.file_out = 'testSetup/MCL900_Modbus_TestResult_' + str(device_number) + '.xlsx'
        self.wb_out = xlsxwriter.Workbook(self.file_out)
        #self.ws_out = self.wb_out.add_worksheet(self.device_id)

        self.device_id = 'ID0' + str(device_number)
        self.ws_in = self.wb_in.sheet_by_name(self.device_id)
        self.ws_out = self.wb_out.add_worksheet(self.device_id)

    def read_float(self, register, func_code, number_of_registers):
        data = self.instrument.read_float(register, func_code, number_of_registers)
        return data

    def get_relays_alarms(self, register_address, number_of_bits):
        data_bits = self.instrument.read_bits(
            register_address, number_of_bits,
            functioncode=Utilities.MODBUS_FUNCTION_RELAYS_ALARMS_REGISTERS)
        print(str(data_bits))

    def get_data_status(self, register_address, func_code, number_of_registers):
        register_data = self.instrument.read_registers(
            register_address, number_of_registers, func_code,
            number_of_registers/2, is_float=True)
        #print(str(register_data))
        return register_data

    def get_data_config(self, register_address, func_code, number_of_registers):
        register_data = self.instrument.read_registers(
            register_address, number_of_registers, func_code,
            number_of_registers/2, is_float=False)
        #print(str(register_data))
        return register_data

    def refresh_config(self):
        config_dictionary = self.get_data_config(Utilities.DATA_COND_RES1, Utilities.MODBUS_FUNCTION_CONFIG_REGISTERS, SERIES_900_REGISTER_SIZE)
        for key, value in config_dictionary:
            print(key, ' : ', value)

    def read_sequential_registers(self, function_code, start_address, number_of_registers):
        if function_code == Utilities.MODBUS_FUNCTION_CONFIG_REGISTERS:
            print('read config registers start_address', start_address, 'number_of_registers', number_of_registers)
            register_data = self.get_data_config(start_address, function_code, number_of_registers)
        else:
            print('read data registers start_address', start_address, 'number_of_registers', number_of_registers)
            register_data = self.get_data_status(start_address, function_code, number_of_registers)
        time.sleep(0.2)
        return register_data

    def read_random_registers(self, function_code, random_start=False, random_size=False):
        for x in range(Utilities.DATA_VALUES_COUNT):
            if random_start:
                start_address = random.randint(0, Utilities.DATA_VALUES_COUNT-1)
            else:
                start_address = Utilities.DATA_COND_RES1
            if random_size:
                number_of_registers = random.randint(1, Utilities.DATA_VALUES_COUNT - start_address)
            else:
                number_of_registers = Utilities.DATA_VALUES_COUNT - start_address
            start_address = 2 * start_address
            number_of_registers = 2 * number_of_registers
            print('start_address', start_address, 'number_of_registers', number_of_registers)
            self.get_data_config(start_address, function_code, number_of_registers)
            time.sleep(0.2)

    def test_xls(self):
        """ test os command """
        cwd = os.getcwd()
        # entries = os.listdir(cwd)
        # for entry in entries:
        #     print entry

        """ Test with openpyxl 
        write does not work !
        """
        # file_in_xlsx = 'testSetup/MCL900_Modbus_Registers.xlsx'
        # file_out_xlsx = 'testSetup/MCL900_Modbus_TestResult.xlsx'
        # wb1 = openpyxl.load_workbook(file_in_xlsx)
        # wb2 = openpyxl.load_workbook(file_out_xlsx)
        # ws1 = wb1.get_sheet_by_name('ID01')
        # ws2 = wb2.create_sheet(ws1.title)
        # for row in ws1:
        #     for cell in row:
        #         ws2[cell.coordinate].value = cell.value
        # wb2.close()

        """ Test with xlrd and xlwt """
        file_in = 'testSetup/MCL900_Modbus_Registers.xls'
        file_out = 'testSetup/MCL900_Modbus_TestResult.xls'
        wb_in = xlrd.open_workbook(file_in)
        wb_out = xlwt.Workbook()
        ws_in = wb_in(0)
        ws_out = wb_out(0)

        ws_in = wb_in.sheet_by_name('ID01')
        print '--- Device', ws_in.name
        ws_out = wb_out.add_sheet(ws_in.name)
        ws_out.write(0, 0, ws_in.row_values(0))
        # ws_out.row_values(0).font.bold = True  how do I bold the title row?
        for j in range(0, ws_in.ncols):
            ws_out.col(j).width = 256 * 20
            # how do set format value in the middle ?
            for i in range(1, ws_in.nrows):
                ws_out.write(i, j, ws_in.cell_value(i, j))

        ws_in = wb_in.sheet_by_name('ID02')
        print '--- Device', ws_in.name
        ws_out = wb_out.add_sheet(ws_in.name)
        ws_out.write(0, 0, ws_in.row_values(0))
        # ws_out.row_values(0).font.bold = True  how do I bold the title row?
        for j in range(0, ws_in.ncols):
            ws_out.col(j).width = 256 * 20
            # how do set format value in the middle ?
            for i in range(1, ws_in.nrows):
                ws_out.write(i, j, ws_in.cell_value(i, j))

        wb_out.save(file_out)

    def initialize_sheet_xlwt(self, sheet_name, wb_in, wb_out):
        ws_in = wb_in.sheet_by_name(sheet_name)
        print '--- Device', ws_in.name
        ws_out = wb_out.add_sheet(ws_in.name)
        ws_out.write(0, 0, ws_in.row_values(0))
        # ws_out.row_values(0).font.bold = True  how do I bold the title row?
        for j in range(0, ws_in.ncols):
            ws_out.col(j).width = 256 * 20
            # how do set format value in the middle ?
            for i in range(1, ws_in.nrows):
                ws_out.write(i, j, ws_in.cell_value(i, j))

    def initialize_workbook_xlwt_test(self):
        file_in = 'testSetup/MCL900_Modbus_Registers.xls'
        file_out = 'testSetup/MCL900_Modbus_TestResult.xls'
        wb_in = xlrd.open_workbook(file_in)
        wb_out = xlwt.Workbook()  # using xlwt
        self.initialize_sheet_xlwt('ID01', wb_in, wb_out)
        self.initialize_sheet_xlwt('ID02', wb_in, wb_out)
        wb_out.save(file_out)   # using xlwt

    def initialize_workbook_xlwt(self):
        self.initialize_sheet_xlwt('ID01', self.wb_in, self.wb_out)
        self.initialize_sheet_xlwt('ID02', self.wb_in, self.wb_out)

    def initialize_workbook_xlsxwriter_test(self):
        file_in = 'testSetup/MCL900_Modbus_Registers.xls'
        file_out = 'testSetup/MCL900_Modbus_TestResult.xlsx'
        wb_in = xlrd.open_workbook(file_in)
        ws_in = wb_in.sheet_by_name('ID01')
        wb_out = xlsxwriter.Workbook(file_out)
        ws_out = wb_out.add_worksheet(ws_in.name)

        #cell_format = ws_out.add_format({'bold': True, 'font_color': 'blue'})
        cell_format = wb_out.add_format()
        #cell_format = wb_out.add_format({'bold': False})
        cell_format.set_bold()
        cell_format.set_center_across()
        cell_format.set_text_wrap()
        ws_out.set_column('A:I', 20, cell_format)

        for i in range(0, ws_in.ncols):
            ws_out.write(0, i, ws_in.cell_value(0, i), cell_format)
        wb_out.close()


    def initialize_workbook_xlsxwriter_row0(self, device_id):
        cell_format = self.wb_out.add_format({'bold': True})
        cell_format.set_center_across()
        cell_format.set_text_wrap()
        self.ws_out.set_column('A:J', 20, cell_format)
        for i in range(0, self.ws_in.ncols):
            self.ws_out.write(0, i, self.ws_in.cell_value(0, i), cell_format)

    def initialize_workbook_xlsxwriter_rows(self, device_id):
        cell_format = self.wb_out.add_format({'bold': False})
        cell_format.set_text_wrap()
        cell_format.set_align('Left')
        for j in range(1, self.ws_in.nrows):
            for i in range(0, self.ws_in.ncols):
                self.ws_out.write(j, i, self.ws_in.cell_value(j, i), cell_format)

    def initialize_workbook_xlsxwriter(self, device_id):
        self.initialize_workbook_xlsxwriter_row0(device_id)
        self.initialize_workbook_xlsxwriter_rows(device_id)

    def read_compare_configuration_registers(self):
        register_data = self.read_sequential_registers(Utilities.MODBUS_FUNCTION_CONFIG_REGISTERS,
                                                         Utilities.DATA_COND_RES1, SERIES_900_REGISTER_SIZE)
        # print(str(register_data))
        for i in range(1, len(register_data)):
            self.ws_out.write_number(i, 8, register_data[i])  # save to Read Config column
            if self.ws_in.cell_value(i, 7) == register_data[i]:  # compare Expected Config to Read Config
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'green', 'align': 'center_across'})
                self.ws_out.write_string(i, 9, 'pass', cell_format)  # save result to Compare Config
            else:
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'red', 'align': 'center_across'})
                self.ws_out.write_string(i, 9, 'fail', cell_format)

    def read_compare_data_registers(self):
        register_data = self.read_sequential_registers(Utilities.MODBUS_FUNCTION_DATA_REGISTERS,
                                                         Utilities.DATA_COND_RES1, SERIES_900_REGISTER_SIZE)
        #print(str(register_data))
        for i in range(1, len(register_data)):
            self.ws_out.write_number(i, 4, register_data[i])  # save to Read Data column
            if round(self.ws_in.cell_value(i, 3), 1) == round(register_data[i],
                                                                1):  # compare Expected Data to Read Data
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'green', 'align': 'center_across'})
                self.ws_out.write_string(i, 5, 'pass', cell_format)  # save result to Compare Data
            else:
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'red', 'align': 'center_across'})
                self.ws_out.write_string(i, 5, 'fail', cell_format)


def main():
    port = "COM3"
    baudrate = 19200
    random_size = True
    random_start = True

    device_number = input('Enter Device ID number ')
    device_id = 'ID0' + str(device_number)

    """ Choose 900 Series device to connect as UUT """
    modbus = Modbus_Driver(port, baudrate, device_number)

    #modbus.test_xls()
    #modbus.initialize_workbook_xlwt()
    #modbus.initialize_workbook_xlsxwriter_test()


    """ Test access to Relays and Alarms bits """
    number_of_bits = 6
    #modbus.refreshRelaysAlarms(Utilities.RELAY_1_STATE, number_of_bits)
    modbus.get_relays_alarms(0, number_of_bits)

    number_of_bits = 7
    try:  # Error: illegal bit address
        modbus.get_relays_alarms(0, number_of_bits)
    except Exception as e:
        print(e)

    """ Test access to 900 Series Modbus Configuration Registers """
    # Read Configuration Registers
    ''' still debugging '''
    # modbus.get_data_config(Utilities.DATA_COND_RES1, Utilities.MODBUS_FUNCTION_CONFIG_REGISTERS, SERIES_900_REGISTER_SIZE)
    #modbus.refresh_config()
    time.sleep(0.2)

    # starting at the base address, read until end of configuration registers
    modbus.initialize_workbook_xlsxwriter('ID01')
    modbus.read_compare_configuration_registers()
    modbus.read_compare_data_registers()

    # modbus.wb_out.save(modbus.file_out)    # using xlwt
    modbus.wb_out.close()  # using xlsxwriter

    print 'quick debug exit'
    exit()  # use for quick debug

    # starting random even base address, Read random number of (u_int_32) configuration registers
    modbus.read_random_registers(Utilities.MODBUS_FUNCTION_CONFIG_REGISTERS, random_start, random_size)

    """ Test error condition for Modbus Config Registers """
    number_of_registers = 4
    try:  # Error: illegal data address
        modbus.read_float(Utilities.CONFIG_COND_RES1+1, Utilities.MODBUS_FUNCTION_DATA_REGISTERS, number_of_registers)
    except Exception as e:
        print(e)

    try:  # Error: illegal data address
        modbus.read_float(Utilities.CONFIG_ORP_2 + 2, Utilities.MODBUS_FUNCTION_DATA_REGISTERS, number_of_registers)
    except Exception as e:
        print(e)

    """ Test access to 900 Series Modbus Data Registers """
    # Read as a float, if you need to read a 16 bit register use instrument.read_register()
    number_of_registers = 2
    cond1_status = modbus.read_float(Utilities.DATA_COND_RES1, Utilities.MODBUS_FUNCTION_DATA_REGISTERS, number_of_registers)
    cond1_temperature = modbus.read_float(Utilities.DATA_COND_RES1, Utilities.MODBUS_FUNCTION_DATA_REGISTERS, number_of_registers)

    # Print the values
    print('The cond1 status is: %.1f uS\r' % cond1_status)
    print('The cond1 temperature is: %.1f C\r' % cond1_temperature)

    modbus.get_data_status(Utilities.DATA_COND_RES1, Utilities.MODBUS_FUNCTION_DATA_REGISTERS, SERIES_900_REGISTER_SIZE)

    # starting random even base address, Read until end of configuration registers
    modbus.read_random_registers(Utilities.MODBUS_FUNCTION_DATA_REGISTERS)

    # starting random even base address, Read random number of (u_int_32) configuration registers
    modbus.read_random_registers(Utilities.MODBUS_FUNCTION_DATA_REGISTERS, random_size)

    """ Test error condition for Modbus Data Registers """
    try:  # Error: illegal data address
        modbus.read_float(Utilities.DATA_COND_RES1+1, Utilities.MODBUS_FUNCTION_DATA_REGISTERS, number_of_registers)
    except Exception as e:
        print(e)

    try:  # Error: illegal data address
        modbus.read_float(SERIES_900_REGISTER_SIZE + 2, Utilities.MODBUS_FUNCTION_DATA_REGISTERS, number_of_registers)
    except Exception as e:
        print(e)

    """ Test error report for unsupported Modbus function code """
    try:  # Error: Wrong function code
        modbus.read_float(Utilities.DATA_COND_RES1, 5, number_of_registers)
    except Exception as e:
        print(e)

    print('done Modbus Test Script')

if __name__ == '__main__':
    main()
