#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    MODBUS Connect Root File
"""

__version__ = "$Revision: 1.0.0 $"
__author__ = "Sy Tran"
__status__ = "Internal"
__date__ = "1 March 2021"

import time
import xlrd
import xlsxwriter
import minimalmodbus
import random
import Utilities

READ_RELAY_ALARM = 2  # read 900 Alarms and Relays status = READ_DISCRETE_REGISTERS
READ_CONFIG_REGISTER = 3  # 900S configuration = READ_HOLDING_REGISTER
READ_STATUS_REGISTER = 4  # 900s Status = READ_INPUT_REGISTER

# # Define 900 Series Modbus registers address
MODBUS_900_REGISTER_SIZE = 30
SERIES_900_REGISTER_SIZE = MODBUS_900_REGISTER_SIZE / 2

COND1_STATUS = 0
COND1_TEMPERATURE = 2
COND2_STATUS = 4
COND2_TEMPERATURE = 6
MLC_pH_STATUS = 8
MLC_pH_TEMPERATURE = 10
EXT_pH_ORP_STATUS = 12
EXT_pH_RTD_TEMPERATURE = 14
FLOW_FREQUENCY = 16
FLOW_VOLUME = 18
IN_420_mA = 20
OUT_420_mA = 22
OUT_REC_VOLT = 24
REJECTION_RATIO = 26
ORP2_STATUS = 28
RELAYS_ALARMS_STATUS = 30


class Modbus_Driver:
    def __init__(self, port, baudrate, device_number):
        """ Set up Minimal Modbus """
        self.instrument = minimalmodbus.Instrument(port, device_number, mode="rtu")
        self.instrument.serial.baudrate = baudrate  # Baud
        self.instrument.serial.bytesize = 8
        self.instrument.serial.parity = minimalmodbus.serial.PARITY_EVEN
        self.instrument.serial.stopbits = 1
        self.instrument.serial.timeout = 1  # seconds
        self.instrument.close_port_after_each_call = True  # next 2 lines are good coding practice
        self.instrument.clear_buffers_before_each_transaction = True

        if device_number < 10:
            self.device_id = 'ID0' + str(device_number)
        else:
            self.device_id = 'ID' + str(device_number)

        self.index_misc_test = 0

        """ Intialize Excel Worksheets """
        self.file_in = 'testResults/MCL900_Modbus_Registers.xls'
        self.file_out = 'testResults/MCL900_Modbus_TestResult_' + str(device_number) + '.xlsx'
        self.wb_in = xlrd.open_workbook(self.file_in)
        self.wb_out = xlsxwriter.Workbook(self.file_out)
        self.ws_in = self.wb_in.sheet_by_name(self.device_id)
        self.ws_out = self.wb_out.add_worksheet(self.device_id)
        self.initialize_workbook_xlsxwriter_row0(self.device_id)
        self.initialize_workbook_xlsxwriter_rows(self.device_id)

        """ setup Excel column index for writing to output file """
        self.title_dict = {}
        for col_index in range(self.ws_in.ncols):
            self.title_dict[str(self.ws_in.cell(0, col_index).value)] = str(col_index)
        print self.title_dict

        self.exp_data_colm = int(self.title_dict.get('Expected Data (Dec)'))
        self.read_data_colm = int(self.title_dict.get('Read Data (Dec)'))
        self.compare_data = int(self.title_dict.get('Compare Data'))

        self.exp_config_colm = int(self.title_dict.get('Expected Config (Dec)'))
        self.read_config_colm = int(self.title_dict.get('Read Config (Dec)'))
        self.compare_config = int(self.title_dict.get('Compare Config'))

        self.exp_relay_alarm_colm = int(self.title_dict.get('Expected Relay Alarm Bits'))
        self.read_relay_alarm_colm = int(self.title_dict.get('Read Relay Alarm Bits'))
        self.compare_relay_alarm = int(self.title_dict.get('Compare Relay Alarm Bits'))

        print self.exp_data_colm, self.read_data_colm, self.compare_data
        print self.exp_config_colm, self.read_config_colm, self.compare_config
        print self.exp_relay_alarm_colm, self.read_relay_alarm_colm, self.compare_relay_alarm

    """
    read_float() minimal modbus library function. I use it for testing and debugging purpose
    """
    def read_float(self, register, func_code, number_of_registers):
        data = self.instrument.read_float(register, func_code, number_of_registers)
        return data

    def get_relays_alarms(self, register_address, number_of_bits):
        data_bits = self.instrument.read_bits(register_address, number_of_bits, functioncode=READ_RELAY_ALARM)
        return data_bits

    def get_data_status(self, register_address, func_code, number_of_registers):
        register_data = self.instrument.read_registers(
            register_address, number_of_registers, func_code, number_of_registers/2, is_float=True)
        return register_data

    def get_data_config(self, register_address, func_code, number_of_registers):
        register_data = self.instrument.read_registers(
            register_address, number_of_registers, func_code, number_of_registers/2, is_float=False)
        return register_data

    def refresh_config(self):
        config_dictionary = self.get_data_config(COND1_STATUS, READ_CONFIG_REGISTER, MODBUS_900_REGISTER_SIZE)
        for key, value in config_dictionary:
            print(key, ' : ', value)

    def read_sequential_registers(self, function_code, start_address, number_of_registers):
        if function_code == READ_CONFIG_REGISTER:
            print('read config registers start_address', start_address, 'number_of_registers', number_of_registers)
            register_data = self.get_data_config(start_address, function_code, number_of_registers)
        else:
            print('read data registers start_address', start_address, 'number_of_registers', number_of_registers)
            register_data = self.get_data_status(start_address, function_code, number_of_registers)
        return register_data

    def read_random_registers(self, function_code, random_start=False, random_size=False):
        for x in range(Utilities.DATA_VALUES_COUNT):
            if random_start:
                start_address = random.randint(0, SERIES_900_REGISTER_SIZE - 1)
            else:
                start_address = COND1_STATUS
            if random_size:
                number_of_registers = random.randint(1, SERIES_900_REGISTER_SIZE - start_address)
            else:
                number_of_registers = SERIES_900_REGISTER_SIZE - start_address
            start_address = 2 * start_address
            number_of_registers = 2 * number_of_registers
            print('start_address', start_address, 'number_of_registers', number_of_registers)
            self.get_data_config(start_address, function_code, number_of_registers)

    def initialize_workbook_xlsxwriter_row0(self, device_id):
        cell_format = self.wb_out.add_format({'bold': True})
        cell_format.set_center_across()
        cell_format.set_text_wrap()
        self.ws_out.set_column('A:O', 20, cell_format)
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

    def compare_configuration_registers(self):
        register_data = self.read_sequential_registers(READ_CONFIG_REGISTER, COND1_STATUS, MODBUS_900_REGISTER_SIZE)
        for i in range(0, len(register_data)):
            i1 = i + 1
            self.ws_out.write_number(i1, self.read_config_colm, register_data[i])  # save to Read Config column
            if self.ws_in.cell_value(i1, self.exp_config_colm) == register_data[i]:  # compare Expected Config to Read Config
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'green', 'align': 'center_across'})
                self.ws_out.write_string(i1, self.compare_config, 'pass', cell_format)  # save result to Compare Config
            else:
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'red', 'align': 'center_across'})
                self.ws_out.write_string(i1, self.compare_config, 'fail', cell_format)

    def compare_data_registers(self):
        register_data = self.read_sequential_registers(READ_STATUS_REGISTER, COND1_STATUS, MODBUS_900_REGISTER_SIZE)
        for i in range(0, len(register_data)):
            i1 = i + 1
            self.ws_out.write_number(i1, self.read_data_colm, register_data[i])  # save to Read Data column
            if round(self.ws_in.cell_value(i1, self.exp_data_colm), 0) == round(register_data[i], 0):  # compare Expected Data to Read Data
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'green', 'align': 'center_across'})
                self.ws_out.write_string(i1, self.compare_data, 'pass', cell_format)  # save result to Compare Data
            else:
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'red', 'align': 'center_across'})
                self.ws_out.write_string(i1, self.compare_data, 'fail', cell_format)

    def compare_relay_alarm_bits(self):
        number_of_bits = 6
        data_bits = self.get_relays_alarms(0, number_of_bits)
        for i in range(0, len(data_bits)):
            i1 = i + 1
            self.ws_out.write_number(i1, self.read_relay_alarm_colm, data_bits[i])
            if self.ws_in.cell_value(i1, self.exp_relay_alarm_colm) == data_bits[i]:  # compare Expected Config to Read Config
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'green', 'align': 'center_across'})
                self.ws_out.write_string(i1, self.compare_relay_alarm, 'pass', cell_format)  # save result to Compare Config
            else:
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'red', 'align': 'center_across'})
                self.ws_out.write_string(i1, self.compare_relay_alarm, 'fail', cell_format)

    """ -----------------------------------------------------------------------
    run_error_condition_test()
    Create error conditions to verify 900S catch the error condition and report error back to host
    Step through each commands  
      Function Code 2 = Modbus Read Discrete Register = READ_RELAY_ALARM 
      Function Code 3 = Modbus Read Holding Register = READ_CONFIG_REGISTER 
      Function Code 4 = Modbus Read Input Register = READ_STATUS_REGISTER
    With each command test the following conditions
      Error: illegal data address. Start at odd address 
      Error: illegal data address. Start at out of range register address
      Error: Slave reported illegal data value. Request read beyond register address
      Error: Wrong function code. Request 900S unsupported Modbus function code
    """
    def run_error_condition_test(self):
        """ Test error condition for Modbus Config Registers """
        number_of_registers = 4

        self.index_misc_test += 1
        cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'blue', 'align': 'set_align'})
        self.ws_out.write_string(self.index_misc_test, 0, 'Start at odd address Config Register', cell_format)
        try:  # Error: illegal data address. Start at odd address Config Register
            self.get_data_status(COND1_STATUS + 1, READ_CONFIG_REGISTER, number_of_registers)
        except Exception as e:
            print(e)
            if str(e) == 'Slave reported illegal data address':
                print ' + Pass expected error condition test - Start at odd address Config Register'
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'green', 'align': 'center_across'})
                self.ws_out.write_string(self.index_misc_test, 1, 'Pass', cell_format)
            else:
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'red', 'align': 'center_across'})
                self.ws_out.write_string(self.index_misc_test, 1, 'Fail', cell_format)

        """ Test error condition for Modbus Data Registers """
        self.index_misc_test += 1
        cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'blue', 'align': 'set_align'})
        self.ws_out.write_string(self.index_misc_test, 0, 'Start at odd address Data Register', cell_format)
        try:  # Error: illegal data address. Start at odd address Data Register
            self.get_data_status(COND1_STATUS + 1, READ_STATUS_REGISTER, number_of_registers)
        except Exception as e:
            print(e)
            if str(e) == 'Slave reported illegal data address':
                print ' + Pass expected error condition test - Start at odd address Data Register'
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'green', 'align': 'center_across'})
                self.ws_out.write_string(self.index_misc_test, 1, 'Pass', cell_format)
            else:
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'red', 'align': 'center_across'})
                self.ws_out.write_string(self.index_misc_test, 1, 'Fail', cell_format)

        self.index_misc_test += 1
        cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'blue', 'align': 'set_align'})
        self.ws_out.write_string(self.index_misc_test, 0, 'Start at out of range Config Register address', cell_format)
        try:  # Error: illegal data address. Start at out of range Config Register address
            self.get_data_status(MODBUS_900_REGISTER_SIZE + 2, READ_CONFIG_REGISTER, number_of_registers)
        except Exception as e:
            print(e)
            if str(e) == 'Slave reported illegal data address':
                print ' + Pass expected error condition test - Start at out of range Config Register address'
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'green', 'align': 'center_across'})
                self.ws_out.write_string(self.index_misc_test, 1, 'Pass', cell_format)
            else:
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'red', 'align': 'center_across'})
                self.ws_out.write_string(self.index_misc_test, 1, 'Fail', cell_format)

        self.index_misc_test += 1
        cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'blue', 'align': 'set_align'})
        self.ws_out.write_string(self.index_misc_test, 0, 'Start at out of range Data Register address', cell_format)
        try:  # Error: Slave reported illegal data address. Start at out of range Data Register address
            self.get_data_status(MODBUS_900_REGISTER_SIZE + 2, READ_STATUS_REGISTER, number_of_registers)
        except Exception as e:
            print(e)
            if str(e) == 'Slave reported illegal data address':
                print ' + Pass expected error condition test - Start at out of range Data Register address'
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'green', 'align': 'center_across'})
                self.ws_out.write_string(self.index_misc_test, 1, 'Pass', cell_format)
            else:
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'red', 'align': 'center_across'})
                self.ws_out.write_string(self.index_misc_test, 1, 'Fail', cell_format)

        number_of_registers = 32
        self.index_misc_test += 1
        cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'blue', 'align': 'set_align'})
        self.ws_out.write_string(self.index_misc_test, 0, 'Read beyond Config Register address', cell_format)
        try:  # Error: Slave reported illegal data value. Request read beyond Config Register address
            self.get_data_status(COND1_STATUS, READ_CONFIG_REGISTER, number_of_registers)
        except Exception as e:
            print(e)
            if str(e) == 'Slave reported illegal data value':
                print ' + Pass expected error condition test - Read beyond Config Register address'
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'green', 'align': 'center_across'})
                self.ws_out.write_string(self.index_misc_test, 1, 'Pass', cell_format)
            else:
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'red', 'align': 'center_across'})
                self.ws_out.write_string(self.index_misc_test, 1, 'Fail', cell_format)

        self.index_misc_test += 1
        cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'blue', 'align': 'set_align'})
        self.ws_out.write_string(self.index_misc_test, 0, 'Read beyond Data Register address', cell_format)
        try:  # Error: Slave reported illegal data value. Request read beyond Data Register address
            self.get_data_status(COND1_STATUS, READ_STATUS_REGISTER, number_of_registers)
        except Exception as e:
            print(e)
            if str(e) == 'Slave reported illegal data value':
                print ' + Pass expected error condition test - Read beyond Data Register address'
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'green', 'align': 'center_across'})
                self.ws_out.write_string(self.index_misc_test, 1, 'Pass', cell_format)
            else:
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'red', 'align': 'center_across'})
                self.ws_out.write_string(self.index_misc_test, 1, 'Fail', cell_format)

        """ Test access to Relays and Alarms bits """
        number_of_bits = 7
        self.index_misc_test += 1
        cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'blue', 'align': 'set_align'})
        self.ws_out.write_string(self.index_misc_test, 0, 'Relays & Alarm Request beyond bit address', cell_format)
        try:  # Error: illegal bit address - Request bit beyond legal bit address
            self.get_relays_alarms(0, number_of_bits)
        except Exception as e:
            print(e)
            if str(e) == 'Slave reported illegal data value':
                print ' + Pass expected error condition test - Request bit beyond legal bit address'
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'green', 'align': 'center_across'})
                self.ws_out.write_string(self.index_misc_test, 1, 'Pass', cell_format)
            else:
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'red', 'align': 'center_across'})
                self.ws_out.write_string(self.index_misc_test, 1, 'Fail', cell_format)

        """ Test error report for unsupported Modbus function code """
        self.index_misc_test += 1
        cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'blue', 'align': 'set_align'})
        self.ws_out.write_string(self.index_misc_test, 0, '900S Unsupported Modbus function code', cell_format)
        try:  # Error: Wrong function code. Request 900S unsupported Modbus function code
            self.read_float(COND1_STATUS, 5, number_of_registers)
        except Exception as e:
            print(e)
            # message = str(e)
            # message = message[0:19]
            # if message == 'Wrong function code':
            if str(e)[0:19] == 'Wrong function code':
                print ' + Pass expected error condition test'
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'green', 'align': 'center_across'})
                self.ws_out.write_string(self.index_misc_test, 1, 'Pass', cell_format)
            else:
                cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'red', 'align': 'center_across'})
                self.ws_out.write_string(self.index_misc_test, 1, 'Fail', cell_format)


    """ -----------------------------------------------------------------------
    run_read_sequential_test()
    1. Starting at base address, read until end of configuration registers
    2. Starting at base address, read until end of Data Status registers
    """
    def run_read_sequential_test(self):
        self.index_misc_test += 1
        cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'blue', 'align': 'set_align'})
        self.ws_out.write_string(self.index_misc_test, 0, 'Read Sequential Config Register', cell_format)
        try:
            self.read_sequential_registers(READ_CONFIG_REGISTER, COND1_STATUS, MODBUS_900_REGISTER_SIZE)
            print ' + Pass read sequential Config registers '
            cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'green', 'align': 'center_across'})
            self.ws_out.write_string(self.index_misc_test, 1, 'Pass', cell_format)
        except Exception as e:
            print(e)
            cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'red', 'align': 'center_across'})
            self.ws_out.write_string(self.index_misc_test, 1, 'Fail', cell_format)

        self.index_misc_test += 1
        cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'blue', 'align': 'set_align'})
        self.ws_out.write_string(self.index_misc_test, 0, 'Read Sequential Data Register', cell_format)
        try:
            self.read_sequential_registers(READ_STATUS_REGISTER, COND1_STATUS, MODBUS_900_REGISTER_SIZE)
            print ' + Pass read sequential Data registers '
            cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'green', 'align': 'center_across'})
            self.ws_out.write_string(self.index_misc_test, 1, 'Pass', cell_format)
        except Exception as e:
            print(e)
            cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'red', 'align': 'center_across'})
            self.ws_out.write_string(self.index_misc_test, 1, 'Fail', cell_format)


    """ -----------------------------------------------------------------------
    run_read_random_test()
    1. starting at even base address, Read random number of (u_int_32) configuration registers
    2. starting at even base address, Read random number of (u_int_32) DataStatus registers
    3. starting random even base address, Read random number of (u_int_32) configuration registers
    4. starting random even base address, Read random number of (u_int_32) DataStatus registers
    """
    def run_read_random_test(self):
        random_size = True
        self.read_random_registers(READ_CONFIG_REGISTER, False, random_size)
        self.read_random_registers(READ_STATUS_REGISTER, False, random_size)
        random_start = True
        self.read_random_registers(READ_CONFIG_REGISTER, random_start, random_size)
        self.read_random_registers(READ_STATUS_REGISTER, random_start, random_size)

    """ -----------------------------------------------------------------------
    main()   Run various modbus tests
    Open a reference Excel worksheet, compare read values and store result to output another worksheet
    Run Register Comparison and verify read value and compare to expected value and store result to output
    Run test with error conditions verify 900S reports error
    Run good case condition to verify 900S report status properly
    """
def main():
    port = "COM3"
    baudrate = 19200

    """ Choose 900 Series device to connect as UUT """
    device_number = input('Enter Device ID number ')
    modbus = Modbus_Driver(port, baudrate, device_number)
    #modbus.initialize_workbook_xlsxwriter(modbus.device_id)  # Setup Excel Files


    # print 'quick debug exit'
    # exit()  # use for quick debug

    """ 
    Compare 900S Modbus Registers. Starting at the base address, read until end of configuration registers 
      Function Code 2 = Modbus Read Discrete Register = READ_RELAY_ALARM 
      Function Code 3 = Modbus Read Holding Register = READ_CONFIG_REGISTER 
      Function Code 4 = Modbus Read Input Register = READ_STATUS_REGISTER
    """
    modbus.compare_configuration_registers()
    modbus.compare_data_registers()
    modbus.compare_relay_alarm_bits()

    #print 'quick debug exit'
    #exit()  # use for quick debug

    modbus.ws_out = modbus.wb_out.add_worksheet(modbus.device_id + ' MiscTest')
    cell_format = modbus.wb_out.add_format({'bold': True, 'align': 'center_across'})
    cell_format.set_text_wrap()
    modbus.ws_out.set_column('A:A', 40, cell_format)
    modbus.ws_out.write_string(0, 0, 'Test Name Error Report', cell_format)
    modbus.ws_out.write_string(0, 1, 'Test Result', cell_format)

    print '** Test good cases before run error case'
    modbus.run_read_sequential_test()
    #modbus.run_read_random_test()

    print '** Test error conditions'
    modbus.run_error_condition_test()

    print '** Retest good case to confirm 900S recover'
    modbus.run_read_sequential_test()

    modbus.wb_out.close()  # Save Excel worksheet using xlsxwriter

    print('** Done Modbus Test Script')

if __name__ == '__main__':
    main()
