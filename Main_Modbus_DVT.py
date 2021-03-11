import Modbus_TestLib
import minimalmodbus

def main():
    """ Choose 900 Series device to connect as UUT """
    port_num = input('Enter COM Port Number ')
    port = 'COM'+str(port_num)
    baud_rate = input('Enter Baudrate ')
    parity = minimalmodbus.serial.PARITY_EVEN
    device_number = input('Enter Device ID number ')

    modbus = Modbus_TestLib.Modbus_TestLib(device_number, port, baud_rate, parity)

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

    print '** Test error conditions'
    modbus.run_error_condition_test()
    modbus.unsupported_func_code_test(1)
    modbus.unsupported_func_code_test(5)
    modbus.unsupported_func_code_test(6)

    print '** Retest good case to confirm 900S recover'
    modbus.run_read_sequential_test()

    modbus.wb_out.close()  # Save Excel worksheet using xlsxwriter

    print('** Done Modbus Test Script')

if __name__ == '__main__':
    main()