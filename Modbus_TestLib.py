#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    MODBUS Engineering Design Verification Test Script
"""

__version__ = "$Revision: 1.0.0 $"
__author__ = "Sy Tran"
__status__ = "Internal"
__date__ = "1 March 2021"

import xlrd
import xlsxwriter
import minimalmodbus
import random
import time

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

delay_time = 0.2

class Modbus_TestLib:
    def __init__(self, device_number, port, baudrate=19200, parity='E'):

        """ Set up Minimal Modbus """
        self.instrument = minimalmodbus.Instrument(port, device_number, mode="rtu")
        self.instrument.serial.baudrate = baudrate  # Baud
        self.instrument.serial.bytesize = 8
        self.instrument.serial.parity = parity
        self.instrument.serial.stopbits = 1
        self.instrument.serial.timeout = 1  # seconds
        self.instrument.close_port_after_each_call = True  # next 2 lines are good coding practice
        self.instrument.clear_buffers_before_each_transaction = True

        self.index_misc_test = 0

        if device_number < 10:
            self.device_id = 'ID0' + str(device_number)
        else:
            self.device_id = 'ID' + str(device_number)

        self.f = open('testResults/MCL900_Modbus_TestResult_' + str(device_number) + '.log', 'w')
        message = 'Port: '+str(port) + '   Baud Rate: '+str(baudrate) + '   Parity: '+str(parity) + '\n'
        self.f.write(message)
        
        """ Initialize Excel Worksheets """
        self.file_in = 'testResults/MCL900_Modbus_Registers.xls'
        self.file_out = 'testResults/MCL900_Modbus_TestResult_' + str(device_number) + '.xlsx'
        self.wb_in = xlrd.open_workbook(self.file_in)
        self.wb_out = xlsxwriter.Workbook(self.file_out)
        self.ws_in = self.wb_in.sheet_by_name(self.device_id)
        self.ws_out = self.wb_out.add_worksheet(self.device_id)
        self.initialize_workbook_xlsxwriter_row0(self.device_id)
        self.initialize_workbook_xlsxwriter_rows(self.device_id)

        # save the test interface setup condition to worksheet
        active_row = self.ws_in.nrows + 2
        cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'blue', 'align': 'set_align'})
        self.ws_out.write_string(active_row + 0, 0, 'Port', cell_format)
        self.ws_out.write_string(active_row + 1, 0, 'Baud Rate', cell_format)
        self.ws_out.write_string(active_row + 2, 0, 'Parity', cell_format)
        self.ws_out.write_string(active_row + 0, 1, port, cell_format)
        self.ws_out.write_string(active_row + 1, 1, str(baudrate), cell_format)
        self.ws_out.write_string(active_row + 2, 1, parity, cell_format)

        self.fm_pass = self.wb_out.add_format({'bold': True, 'font_color': 'green'})
        self.fm_fail = self.wb_out.add_format({'bold': True, 'font_color': 'red'})

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

        # print self.exp_data_colm, self.read_data_colm, self.compare_data
        # print self.exp_config_colm, self.read_config_colm, self.compare_config
        # print self.exp_relay_alarm_colm, self.read_relay_alarm_colm, self.compare_relay_alarm

    """ Copy Row 0 as the column's title to output worksheet """
    def initialize_workbook_xlsxwriter_row0(self, device_id):
        cell_format = self.wb_out.add_format({'bold': True})
        cell_format.set_center_across()
        cell_format.set_text_wrap()
        self.ws_out.set_column('A:O', 20, cell_format)
        for j in range(0, self.ws_in.ncols):
            self.ws_out.write(0, j, self.ws_in.cell_value(0, j), cell_format)

    """ Copy expected values to output worksheet """
    def initialize_workbook_xlsxwriter_rows(self, device_id):
        cell_format = self.wb_out.add_format({'bold': False})
        cell_format.set_text_wrap()
        cell_format.set_align('Left')
        for i in range(1, self.ws_in.nrows):
            for j in range(0, self.ws_in.ncols):
                self.ws_out.write(i, j, self.ws_in.cell_value(i, j), cell_format)

    def initialize_workbook_xlsxwriter(self, device_id):
        self.initialize_workbook_xlsxwriter_row0(device_id)
        self.initialize_workbook_xlsxwriter_rows(device_id)

    def log_misc_test(self, message, start_addr, number_of_registers):
        self.index_misc_test += 1
        cell_format = self.wb_out.add_format({'bold': True, 'font_color': 'blue', 'align': 'set_align'})
        self.ws_out.write(self.index_misc_test, 0, message, cell_format)
        self.ws_out.write(self.index_misc_test, 1, start_addr, cell_format)
        self.ws_out.write(self.index_misc_test, 2, number_of_registers, cell_format)
        self.ws_out.write(self.index_misc_test, 3, 'Error Reported', cell_format)

    """
    read_float() minimal modbus library function. I use it for testing and debugging purpose
    """
    def read_float(self, register, func_code, number_of_registers):
        data = self.instrument.read_float(register, func_code, number_of_registers)
        return data

    """ -----------------------------------------------------------------------
    This code intention was to reuse the same minimal modbus library used in modbus-connect project.
    The modbus-connect project modified the minimalmodbus.py file made it deviate from the standard library.
    To be compatible with the modified minimalmodbus.py, these baseline methods are leveraged from
    modbus-connect project, NetworkStatusPanel.py file. Remaining methods built on top of these baseline methods. 
      get_relays_alarms()
      get_data_status()
      get_data_config()
      refresh_config()
    """
    def get_relays_alarms(self, register_address, num_bits):
        data_bits = self.instrument.read_bits(register_address, num_bits, functioncode=READ_RELAY_ALARM)
        time.sleep(delay_time)
        return data_bits

    def get_data_status(self, register_address, func_code, number_of_registers):
        register_data = self.instrument.read_registers(
            register_address, number_of_registers, func_code, number_of_registers/2, is_float=True)
        time.sleep(delay_time)
        return register_data

    def get_data_config(self, register_address, func_code, number_of_registers):
        register_data = self.instrument.read_registers(
            register_address, number_of_registers, func_code, number_of_registers/2, is_float=False)
        time.sleep(delay_time)
        return register_data

    def refresh_config(self):
        config_dictionary = self.get_data_config(COND1_STATUS, READ_CONFIG_REGISTER, MODBUS_900_REGISTER_SIZE)
        for key, value in config_dictionary:
            print(key, ' : ', value)

    """ -----------------------------------------------------------------------
    Group tests sequences into various methods below 
    """
    def read_sequential(self, function_code, start_addr, number_of_registers):
        if function_code == READ_CONFIG_REGISTER:
            register_data = self.get_data_config(start_addr, function_code, number_of_registers)
        else:
            register_data = self.get_data_status(start_addr, function_code, number_of_registers)
        time.sleep(delay_time)
        return register_data

    def read_sequential_registers(self, function_code, start_addr, number_of_registers):
        print 'Start Read Sequential Registers with Function Code: '+str(function_code)
        result_colm = 3
        try:
            if function_code == READ_CONFIG_REGISTER:
                register_data = self.get_data_config(start_addr, function_code, number_of_registers)
                msg0 = 'Read Sequential Config Register FuncCode ' + str(function_code)
                self.log_misc_test(msg0, start_addr, number_of_registers)
            else:
                register_data = self.get_data_status(start_addr, function_code, number_of_registers)
                msg0 = ' Read Sequential Data Register FuncCode ' + str(function_code)
                self.log_misc_test(msg0, start_addr, number_of_registers)
            msg1 = msg0 + ' start_addr:'+str(start_addr) + ' number_of_registers:'+str(number_of_registers)

            self.ws_out.write_string(self.index_misc_test, result_colm, 'Pass', self.fm_pass)
            msg2 = ' Pass -- ' + msg1
        except Exception as e:
            print(e)
            self.ws_out.write_string(self.index_misc_test, result_colm, 'Fail', self.fm_fail)
            msg2 = ' Fail -- ' + msg1
        print msg2 + '\n'
        self.f.write(msg2 + '\n')
        time.sleep(delay_time)
        return register_data

    def read_random_registers(self, function_code, random_start=False, random_size=False):
        msg0 = 'Start Read Random Registers with Function Code: '+str(function_code)
        print msg0
        self.f.write(msg0 + '\n')

        result_colm = 3
        for x in range(SERIES_900_REGISTER_SIZE):
            if random_start:
                start_addr = random.randint(0, SERIES_900_REGISTER_SIZE - 1)
            else:
                start_addr = COND1_STATUS
            if random_size:
                number_of_registers = random.randint(1, SERIES_900_REGISTER_SIZE - start_addr)
            else:
                number_of_registers = SERIES_900_REGISTER_SIZE - start_addr
            start_addr = 2 * start_addr
            number_of_registers = 2 * number_of_registers

            try:
                if function_code == READ_CONFIG_REGISTER:
                    msg1 = ' Read Random Config Register FuncCode ' + str(function_code)
                    self.log_misc_test(msg1, start_addr, number_of_registers)
                    register_data = self.get_data_config(start_addr, function_code, number_of_registers)
                else:
                    msg1 = ' Read Random Data Register FuncCode ' + str(function_code)
                    self.log_misc_test(msg1, start_addr, number_of_registers)
                    register_data = self.get_data_status(start_addr, function_code, number_of_registers)
                self.ws_out.write_string(self.index_misc_test, result_colm, 'Pass', self.fm_pass)
                msg2 = ' Pass -- ' + msg1 + ' start_addr:' + str(start_addr) + ' number_of_registers:' + str(number_of_registers)
            except Exception as e:
                print(e)
                self.ws_out.write_string(self.index_misc_test, result_colm, 'Fail', self.fm_fail)
                msg2 = ' Fail -- ' + msg1
            print msg2 + '\n'
            self.f.write(msg2 + '\n')
            time.sleep(delay_time)
            return register_data

    def compare_configuration_registers(self):
        self.f.write('Start Compare Config Regs \n')
        register_data = self.read_sequential(READ_CONFIG_REGISTER, COND1_STATUS, MODBUS_900_REGISTER_SIZE)
        for i in range(0, len(register_data)):
            i1 = i + 1
            self.ws_out.write_number(i1, self.read_config_colm, register_data[i])  # save to Read Config column
            if self.ws_in.cell_value(i1, self.exp_config_colm) == register_data[i]:  # compare Expected Config to Read Config
                self.ws_out.write_string(i1, self.compare_config, 'Pass', self.fm_pass)  # save result to Compare Config
                msg = ' Read Config Reg: Pass,  Addr:'+str(i1)
            else:
                self.ws_out.write_string(i1, self.compare_config, 'Fail', self.fm_fail)
                msg = ' Read Config Reg: Fail,  Addr:'+str(i1)
            self.f.write(msg + '\n')

    def compare_data_registers(self):
        register_data = self.read_sequential(READ_STATUS_REGISTER, COND1_STATUS, MODBUS_900_REGISTER_SIZE)
        for i in range(0, len(register_data)):
            i1 = i + 1
            self.ws_out.write_number(i1, self.read_data_colm, register_data[i])  # save to Read Data column
            if round(self.ws_in.cell_value(i1, self.exp_data_colm), 0) == round(register_data[i], 0):  # compare Expected Data to Read Data
                self.ws_out.write_string(i1, self.compare_data, 'pass', self.fm_pass)  # save result to Compare Data
                msg = ' Pass -- Read Data Reg,  Addr:'+str(i1)
            else:
                self.ws_out.write_string(i1, self.compare_data, 'fail', self.fm_fail)
                msg = ' Fail -- Read Data Reg,  Addr:'+str(i1)
            self.f.write(msg + '\n')

    def compare_relay_alarm_bits(self):
        num_bits = 6
        data_bits = self.get_relays_alarms(0, num_bits)
        for i in range(0, len(data_bits)):
            i1 = i + 1
            self.ws_out.write_number(i1, self.read_relay_alarm_colm, data_bits[i])
            if self.ws_in.cell_value(i1, self.exp_relay_alarm_colm) == data_bits[i]:
                self.ws_out.write_string(i1, self.compare_relay_alarm, 'pass', self.fm_pass)
                msg = ' Pass -- Read Discrete,  Addr:'+str(i1)
            else:
                self.ws_out.write_string(i1, self.compare_relay_alarm, 'fail', self.fm_fail)
                msg = ' Fail -- Read Discrete,  Addr:'+str(i1)
            self.f.write(msg + '\n')

    """ -----------------------------------------------------------------------
    run_read_sequential_test()
    1. Starting at base address, read until end of configuration registers
    2. Starting at base address, read until end of Data Status registers
    """
    def run_read_sequential_test(self):
        self.read_sequential_registers(READ_CONFIG_REGISTER, COND1_STATUS, MODBUS_900_REGISTER_SIZE)
        self.read_sequential_registers(READ_STATUS_REGISTER, COND1_STATUS, MODBUS_900_REGISTER_SIZE)

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
        result_colm = 4
        num_regs = 8
        start_addr = COND1_STATUS + 1

        """ 
        Error condition: Start at odd address 
        """
        msg0 = 'Config Register starts at odd address'
        msg00 = msg0 + ' -- Start Addr:'+str(start_addr) + 'Number of Regs:'+str(num_regs)
        self.f.write(msg00 + '\n')
        self.log_misc_test(msg0, start_addr, num_regs)
        try:  # Error: illegal data address. Start at odd address Config Register
            self.get_data_status(start_addr, READ_CONFIG_REGISTER, num_regs)
        except Exception as e:
            print(e)
            if str(e) == 'Slave reported illegal data address':
                self.ws_out.write_string(self.index_misc_test, result_colm, 'Pass', self.fm_pass)
                msg1 = ' Pass -- Config Register return with report illegal data address'
            else:
                self.ws_out.write_string(self.index_misc_test, result_colm, 'Fail', self.fm_fail)
                msg1 = ' Fail -- Config Register return with report illegal data address'
            print msg1
            self.f.write(msg1 + '\n')

        msg0 = 'Data Register starts at odd address'
        msg00 = msg0 + ' -- Start Addr:'+str(start_addr) + 'Number of Regs:'+str(num_regs)
        self.f.write(msg00 + '\n')
        self.log_misc_test(msg0, start_addr, num_regs)
        try:  # Error: illegal data address. Start at odd address Data Register
            self.get_data_status(start_addr, READ_STATUS_REGISTER, num_regs)
        except Exception as e:
            print(e)
            if str(e) == 'Slave reported illegal data address':
                self.ws_out.write_string(self.index_misc_test, result_colm, 'Pass', self.fm_pass)
                msg1 = ' Pass -- Data Register return with report illegal data address'
            else:
                self.ws_out.write_string(self.index_misc_test, result_colm, 'Fail', self.fm_fail)
                msg1 = ' Fail -- Data Register return with report illegal data address'
            print msg1
            self.f.write(msg1 + '\n')

        """ 
        Error condition: Start at out of range 
        """
        start_addr = MODBUS_900_REGISTER_SIZE + 2
        msg0 = 'Config Register starts at out of range'
        msg00 = msg0 + ' -- Start Addr:'+str(start_addr) + 'Number of Regs:'+str(num_regs)
        self.f.write(msg00 + '\n')
        self.log_misc_test(msg0, start_addr, num_regs)
        try:  # Error: illegal data address. Start at out of range Config Register address
            self.get_data_status(start_addr, READ_CONFIG_REGISTER, num_regs)
        except Exception as e:
            print(e)
            if str(e) == 'Slave reported illegal data address':
                self.ws_out.write_string(self.index_misc_test, result_colm, 'Pass', self.fm_pass)
                msg1 = ' Pass -- Config Register return with report out of range address'
            else:
                self.ws_out.write_string(self.index_misc_test, result_colm, 'Fail', self.fm_fail)
                msg1 = ' Fail -- Config Register return with report out of range address'
            print msg1
            self.f.write(msg1 + '\n')

        msg0 = 'Data Register starts at out of range'
        msg00 = msg0 + ' -- Start Addr:' + str(start_addr) + 'Number of Regs:' + str(num_regs)
        self.f.write(msg00 + '\n')
        self.log_misc_test(msg0, start_addr, num_regs)
        try:  # Error: Slave reported illegal data address. Start at out of range Data Register address
            self.get_data_status(MODBUS_900_REGISTER_SIZE + 2, READ_STATUS_REGISTER, num_regs)
        except Exception as e:
            print(e)
            if str(e) == 'Slave reported illegal data address':
                self.ws_out.write_string(self.index_misc_test, result_colm, 'Pass', self.fm_pass)
                msg1 = ' Pass -- Data Register return with report out of range address'
            else:
                self.ws_out.write_string(self.index_misc_test, result_colm, 'Fail', self.fm_fail)
                msg1 = ' Fail -- Data Register return with report out of range address'
            print msg1
            self.f.write(msg1 + '\n')

        """ 
        Error condition: Read beyond address range 
        """
        start_addr = COND1_STATUS
        num_regs = 32
        msg0 = 'Config Register Read beyond last address'
        msg00 = msg0 + ' -- Start Addr:' + str(start_addr) + 'Number of Regs:' + str(num_regs)
        self.f.write(msg00 + '\n')
        self.log_misc_test(msg0, start_addr, num_regs)
        try:  # Error: Slave reported illegal data value. Request read beyond Config Register address
            self.get_data_status(start_addr, READ_CONFIG_REGISTER, num_regs)
        except Exception as e:
            print(e)
            if str(e) == 'Slave reported illegal data value':
                self.ws_out.write_string(self.index_misc_test, result_colm, 'Pass', self.fm_pass)
                msg1 = ' Pass -- Config Register return with report Read beyond last address'
            else:
                self.ws_out.write_string(self.index_misc_test, result_colm, 'Fail', self.fm_fail)
                msg1 = ' Fail -- Config Register return with report Read beyond last address'
            print msg1
            self.f.write(msg1 + '\n')
            
        msg0 = 'Data Register Read beyond last address'
        msg00 = msg0 + ' -- Start Addr:' + str(start_addr) + 'Number of Regs:' + str(num_regs)
        self.f.write(msg00 + '\n')
        self.log_misc_test(msg0, start_addr, num_regs)
        try:  # Error: Slave reported illegal data value. Request read beyond Data Register address
            self.get_data_status(start_addr, READ_STATUS_REGISTER, num_regs)
        except Exception as e:
            print(e)
            if str(e) == 'Slave reported illegal data value':
                self.ws_out.write_string(self.index_misc_test, result_colm, 'Pass', self.fm_pass)
                msg1 = ' Pass -- Data Register return with report Read beyond last address'
            else:
                self.ws_out.write_string(self.index_misc_test, result_colm, 'Fail', self.fm_fail)
                msg1 = ' Fail -- Data Register return with report Read beyond last address'
            print msg1
            self.f.write(msg1 + '\n')
            
        num_bits = 7
        msg0 = 'Relays & Alarm Read beyond last bit address'
        msg00 = msg0 + ' -- Start Addr:' + str(start_addr) + 'Number of Regs:' + str(num_regs)
        self.f.write(msg00 + '\n')
        self.log_misc_test(msg0, start_addr, num_regs)
        try:  # Error: illegal bit address - Request bit beyond legal bit address
            self.get_relays_alarms(0, num_bits)
        except Exception as e:
            print(e)
            if str(e) == 'Slave reported illegal data value':

                self.ws_out.write_string(self.index_misc_test, result_colm, 'Pass', self.fm_pass)
                msg1 = ' Pass -- Relays & Alarm return with report Read beyond last bit'
            else:
                self.ws_out.write_string(self.index_misc_test, result_colm, 'Fail', self.fm_fail)
                msg1 = ' Fail -- Relays & Alarm return with report Read beyond last bit'
            print msg1
            self.f.write(msg1 + '\n')

    """  Receive Modbus Function code and read a bounded starting register address """
    def unsupported_func_code_test(self, func_code):
        result_colm = 4
        num_regs = 10
        start_addr = COND1_STATUS
        msg0 = '900S Unsupported function code:'+ str(func_code)
        msg00 = msg0 + ' -- Start Addr:' + str(start_addr) + 'Number of Regs:' + str(num_regs)
        self.f.write(msg00 + '\n')
        self.log_misc_test(msg0, start_addr, num_regs)
        try:  # Error: Wrong function code. Request 900S unsupported Modbus function code
            self.read_float(start_addr, func_code, num_regs)
        except Exception as e:
            print(e)
            # message = str(e)
            # message = message[0:19]
            # if message == 'Wrong function code':
            if str(e)[0:19] == 'Wrong function code':
                self.ws_out.write_string(self.index_misc_test, result_colm, 'Pass', self.fm_pass)
                msg1 = ' Pass -- return with Report Unsupported function code '
            else:
                self.ws_out.write_string(self.index_misc_test, result_colm, 'Fail', self.fm_fail)
                msg1 = ' Fail -- return with Report Unsupported function code '
            print msg1
            self.f.write(msg1 + '\n')

    """ 
    Modbus Read Communication Statistic Collection 
    """
    def collect_statistic_communication_read(self, loop_size, function_code=READ_STATUS_REGISTER):
        print 'Start Collecting Statistic Communication Read'
        passed_count = 0
        failed_count = 0
        number_of_reads = MODBUS_900_REGISTER_SIZE  # = 15
        total_reads = number_of_reads * loop_size
        stat_dict = {}
        for loop_count in range(0, loop_size):
            for x in range(number_of_reads):
                start_addr = random.randint(0, SERIES_900_REGISTER_SIZE - 1)
                num_regs = random.randint(1, SERIES_900_REGISTER_SIZE - start_addr)
                start_addr = 2 * start_addr
                num_regs = 2 * num_regs
                try:
                    if function_code == READ_CONFIG_REGISTER:
                        self.get_data_config(start_addr, function_code, num_regs)
                    else:
                        self.get_data_status(start_addr, function_code, num_regs)
                    passed_count += 1
                except Exception as e:
                    print(e)
                    failed_count += 1
                    stat_dict[failed_count] = loop_count  # capture when the failure occurred
            print ('Loop Count:', loop_count, ' Passed Count:', passed_count)

        """
        Create Worksheet to collect Statistic
        """
        self.ws_out = self.wb_out.add_worksheet(self.device_id + ' Statistic Test')
        cell_format = self.wb_out.add_format({'bold': True, 'align': 'center_across'})

        """ Setup Row 0 Title for Over All Statistic """
        self.ws_out.set_column('A:D', 20, cell_format)
        self.ws_out.write_string(0, 0, 'Total Tests Count', cell_format)
        self.ws_out.write_string(0, 1, 'Number of Passed', cell_format)
        self.ws_out.write_string(0, 2, 'Number of Failed', cell_format)
        self.ws_out.write_string(0, 3, '% Passed', cell_format)
        """ Row 1 Data of Over All Statistic """
        percent_passed = (100 * passed_count) / total_reads
        self.ws_out.write_number(1, 0, total_reads)
        self.ws_out.write_number(1, 1, passed_count)
        self.ws_out.write_number(1, 2, failed_count)
        self.ws_out.write_number(1, 3, percent_passed)

        """ Skip Row 2, From Row 3 and on ward save detail data  """
        row = 3
        fm_3 = self.wb_out.add_format({'bold': True})
        self.ws_out.write(row, 0, 'Failed Occurred', fm_3)  # Setup Title for capture Failed Cases
        self.ws_out.write(row, 1, 'Failed at Loop Count', fm_3)
        self.ws_out.write(row+1, 0, 'None', fm_3)
        self.ws_out.write(row+1, 1, 'None', fm_3)

        order = sorted(stat_dict.keys())
        for key in order:
            row += 1
            self.ws_out.write_number(row, 0, key, fm_3)
            self.ws_out.write_number(row, 1, stat_dict[key], fm_3)

        print 'Done Collecting Statistic Communication Read'

    """ -----------------------------------------------------------------------
    main()   Run various modbus tests
    Open a reference Excel worksheet, compare read values and store result to output another worksheet
    Run Register Comparison and verify read value and compare to expected value and store result to output
    Run test with error conditions verify 900S reports error
    Run good case condition to verify 900S report status properly
    """
def main():


    """ Choose 900 Series device to connect as UUT """
    # port_num = input('Enter COM Port Number ')
    # port = 'COM' + str(port_num)
    # baud_rate = input('Enter Baudrate ')
    port = 'COM3'
    baud_rate = 19200
    parity = minimalmodbus.serial.PARITY_EVEN
    device_number = input('Enter Device ID number ')

    modbus = Modbus_TestLib(device_number, port, baud_rate, parity)

    """ 
    Compare 900S Modbus Registers. Starting at the base address, read until end of configuration registers 
      Function Code 2 = Modbus Read Discrete Register = READ_RELAY_ALARM 
      Function Code 3 = Modbus Read Holding Register = READ_CONFIG_REGISTER 1
      Function Code 4 = Modbus Read Input Register = READ_STATUS_REGISTER
    """
    modbus.compare_configuration_registers()
    modbus.compare_data_registers()
    modbus.compare_relay_alarm_bits()

    # Test condition to capture delay time between commands (timing show delays between 160mS to 180 mS)
    # for i in range(6):
    #     modbus.compare_data_registers()
    #     modbus.compare_relay_alarm_bits()
    #     modbus.compare_data_registers()
    #     modbus.compare_relay_alarm_bits()

    # modbus.f.close()
    # modbus.wb_out.close()
    # print 'quick debug exit'
    # exit()  # use for quick debug

    """ Switch to MiscTest worksheet """
    modbus.ws_out = modbus.wb_out.add_worksheet(modbus.device_id + ' MiscTest')
    cell_format = modbus.wb_out.add_format({'bold': True, 'align': 'center_across'})
    cell_format.set_text_wrap()
    modbus.ws_out.set_column('A:A', 40, cell_format)
    modbus.ws_out.set_column('B:C', 10, cell_format)
    modbus.ws_out.set_column('D:E', 15, cell_format)
    modbus.ws_out.write_string(0, 0, 'Test Name Error Report', cell_format)
    modbus.ws_out.write_string(0, 1, 'Start Address', cell_format)
    modbus.ws_out.write_string(0, 2, 'Number of Registers', cell_format)
    modbus.ws_out.write_string(0, 3, 'Test Result', cell_format)
    modbus.ws_out.write_string(0, 4, 'Error Reported', cell_format)

    print '** Test good cases before run error case'
    modbus.run_read_sequential_test()
    modbus.run_read_random_test()

    # modbus.f.close()
    # modbus.wb_out.close()
    # print 'quick debug exit'
    # exit()  # use for quick debug

    print '** Test error conditions'
    modbus.run_error_condition_test()
    modbus.unsupported_func_code_test(1)
    modbus.unsupported_func_code_test(5)
    modbus.unsupported_func_code_test(6)

    print '** Retest good case to confirm 900S recover'
    modbus.run_read_sequential_test()

    # modbus.f.close()
    # modbus.wb_out.close()
    # print 'quick debug exit'
    # exit()  # use for quick debug

    # function_code = READ_CONFIG_REGISTER
    function_code = READ_STATUS_REGISTER
    loop_size = 10
    modbus.collect_statistic_communication_read(loop_size, function_code)

    modbus.f.close()
    modbus.wb_out.close()  # Save Excel worksheet using xlsxwriter
    print('** Done Modbus Test Script')

if __name__ == '__main__':
    main()
