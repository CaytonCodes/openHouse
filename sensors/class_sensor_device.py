#!/usr/bin/env python

from datetime import datetime
from _common_funcs import _settings_update, _error_builder
from comms.class_response import Response


DEFAULT_BUS_NUM = 1
DEFAULT_ADDRESS = 0x27
DEFAULT_DELAY = 1
DEFAULT_NULL_CHAR = None
DEFAULT_ENCODING = 'bytes'
DEFAULT_BUFFER_SIZE = 31
DEFAULT_BLANK_READING = '-'


class SensorDevice:
  def __init__(self, sensorName = '', args = {}, comm = None):
    self.settings = {
      'PROTOCOL': None,
      'MODULE': None,
      'PROTOCOL_ARGS': {
        'I2C_ADDRESS': DEFAULT_ADDRESS,
        'I2C_BUS_NUM': DEFAULT_BUS_NUM,
        'STD_DELAY': DEFAULT_DELAY,
        'ENCODING': DEFAULT_ENCODING,
        'NULL_CHAR': DEFAULT_NULL_CHAR,
      },
      'COMMANDS': {
        'READ': {
          'CODE': 'R',
          'DELAY': None,
          'LENGTH': DEFAULT_BUFFER_SIZE,
          'UNIT': '',
        },
        'CAL': [{
          'CODE': None,
          'DELAY': None,
          'LENGTH': None,
        }]
      }
    }
    _settings_update(self.settings, args)
    self.sensorName = sensorName
    self.comm = comm
    # self.delay = self.settings.get('PROTOCOL_ARGS', {}).get('STD_DELAY', DEFAULT_DELAY)
    self.protocol = self.settings.get('PROTOCOL', None)
    # self.address = self.settings.get('PROTOCOL_ARGS', {}).get('I2C_ADDRESS', DEFAULT_ADDRESS)
    self.lastReadCall = None
    self.prep_sensor()
    self.response = self._prep_request()

  # def get_setting(self, setting, default = None):
  #   if setting in self.settings:
  #     return self.settings.get(setting, default)
  #   else:
  #     return default

  # def _handle_module(self, module, settings = None):
  #   if not settings:
  #     settings = self.settings
  #   presets = preset_sensor_modules.get(module, {})
  #   if presets.get('MODULE', None):
  #     self._handle_module(presets['MODULE'], presets)
  #   _settings_update(settings, presets)
  #   settings['MODULE'] = module

  def prep_sensor(self):
    if self.settings.get('PROTOCOL', None) == 'I2C' and self.comm:
      pass
      # self._i2c_prep_sensor()
    else:
      raise Exception(error_builder('Unknown protocol: ' + self.settings.get('PROTOCOL', None) + ' with comm: ' + self.comm, self.sensorName, None))

  # def _i2c_prep_sensor(self):
  #   args = self.settings.get('PROTOCOL_ARGS', {})
  #   # args['READ_COMMAND'] = self.settings.get('COMMANDS', {}).get('READ', {})
  #   # args['DEVICE_NAME'] = self.sensorName
  #   self.comm = I2CDevice(args)

  # def get_reading(self):
  #   if self.settings.get('PROTOCOL', None) == 'I2C':
  #     return self._i2c_get_reading()
  #   else:
  #     raise Exception(error_builder('Unknown protocol: ' + self.settings.get('PROTOCOL', None), self.sensorName, None))

  # def _i2c_get_reading(self):
  #   cmd, delay = self._i2c_commands('READ')
  #   response = self.comm.query(cmd, delay)
  #   if hasattr(readCommand, 'unit'):
  #     response.set_unit(readCommand['unit'])
  #   return response

  def _prep_request(self):
    args = {
      'deviceName': self.sensorName,
      'protocol': self.settings.get('PROTOCOL_ARGS', {})
    }
    args['protocol']['type'] = self.settings.get('PROTOCOL', None)
    return Response(args)

  def _set_command(self, cmd, delay = None):
    unit = None
    if cmd == self.settings.get('COMMANDS', {}).get('READ', {}).get('CODE', 'wackyDefaultThatWouldNeverBeUsed9001'):
      unit = self.settings.get('COMMANDS', {}).get('READ', {}).get('UNIT', '')
      delay = self.settings.get('COMMANDS', {}).get('READ', {}).get('DELAY', None)
    self.response.recycle()
    self.response.set_cmd(cmd, unit, delay)

  def _write_command(self, cmd, delay = None):
    self._set_command(cmd, delay)
    self.comm.write(self.response)

  # def _i2c_commands(self, commandName):
  #   if commandName in self.settings.get('COMMANDS', {}):
  #     cmd = self.settings.get('COMMANDS', {}).get(commandName, {}).get('CODE', '')
  #     delay = self.settings.get('COMMANDS', {}).get(commandName, {}).get('DELAY', None)
  #     delay = delay if delay else self.delay
  #     return cmd, delay
  #   else:
  #     raise Exception(error_builder('Unknown command: ' + commandName, self.sensorName, None))

  def parallel_read(self):
    # dataOut = False
    # timeNow = datetime.now()
    # if self.lastReadCall and timeNow - self.lastReadCall < self.delay:
    #   return False
    # if self.lastReadCall:
    #   self.response = self.comm.read(self.response)
    #   dataOut = self.response.get_data()
    # cmd = self.settings.get('COMMANDS', {}).get('READ', {}).get('CODE', '')
    # self._write_command(cmd)
    # self.lastReadCall = timeNow
    # return dataOut
    cmd = self.settings.get('COMMANDS', {}).get('READ', {}).get('CODE', '')
    if self.response.inputCmd != cmd:
      self._set_command(cmd)
    return self.comm.parallel_read(self.response)

  def query(self, command, delay = None):
    self._set_command(command, delay)
    return self.comm.query(self.response)

  #   if self.settings.get('PROTOCOL', None) == 'I2C':
  #     return self._i2c_query(command, delay)
  #   else:
  #     raise Exception(error_builder('Unknown protocol: ' + self.settings.get('PROTOCOL', 'Unknown', self.sensorName, None)))

  # def _i2c_query(self, command, delay = None):
  #   if not delay or delay < 0:
  #     delay = self.delay
  #   encoding = self.settings.get('PROTOCOL_ARGS', {}).get('ENCODING', DEFAULT_ENCODING)
  #   nullChar = self.settings.get('PROTOCOL_ARGS', {}).get('NULL_CHAR', DEFAULT_NULL_CHAR)
  #   return self.comm.query(self.address, command, delay, encoding, nullChar)
