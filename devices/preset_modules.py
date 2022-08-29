#!/usr/bin/env python

from devices.class_comm_device import I2CDevice
import mcp9600
from interface.display.display_presets.class_pcf8574 import PCF8574

class AtlasSciEZODevice(I2CDevice):
  def __init__(self, args, deviceName = 'AtlasSciEZO', commManager = None):
    args['BUFFER_SIZE'] = 32
    args['DELAY'] = 1
    args['BLANK_READING'] = '-'
    args['ERROR_READINGS'] = ['0.000', '']
    args['COMMANDS'] = {
      'READ': {
        'CMD': 'R',
        'DELAY': 0.9,
      },
    }
    super().__init__(args, deviceName, commManager)

  def encode(self, cmd):
    cmd += '\x00'
    return cmd.encode('latin-1')

  def decode(self, data):
    statusCode = int(data[0])
    data = data[1:].strip().strip(bytes('\x00', 'latin-1')).decode('latin-1')
    return data, statusCode

  def command_out(self, cmd):
    return self.commManager.write_io(self.address, cmd)

  def get_reading(self):
    return self.commManager.read_io(self.address, self.byteCount)

class AtlasSciEZOPH(AtlasSciEZODevice):
  def __init__(self, args, deviceName = 'AtlasSciEZOPH', commManager = None):
    args['I2C_ADDRESS'] = 0x63
    args['UNIT'] = 'pH'
    super().__init__(args, deviceName, commManager)

class MCP9600(I2CDevice):
  def __init__(self, args, deviceName = 'MCP9600', commManager = None):
    args['I2C_ADDRESS'] = 0x60
    args['BUFFER_SIZE'] = 3
    args['DELAY'] = 0
    args['BLANK_READING'] = '-'
    args['ERROR_READINGS'] = ['0.000', '']
    args['UNIT'] = '°C'
    args['COMMANDS'] = {
      'READ': {
        'CMD': 0x00,
        'DELAY': 0.1,
      },
    }
    super().__init__(args, deviceName, commManager)
    self.mcp9600 = mcp9600.MCP9600(self.settings.get('I2C_ADDRESS', 0x60))

  def get_reading(self):
    return self.mcp9600.get_hot_junction_temperature()

  def command_out(self,cmd):
    return

preset_modules = {
  'AtlasSciEZOPH': AtlasSciEZOPH,
  'MCP9600': MCP9600,
  'PCF8574': PCF8574,
}
