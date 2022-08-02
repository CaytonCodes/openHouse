#!/usr/bin/env python

from datetime import datetime
from comms.class_i2c_device import I2CDevice as I2CDevice
from _common_funcs import settings_update, error_builder
from sensors.preset_sensor_modules import preset_sensor_modules

class SensorDevice:
  def __init__(self, sensorName = '', args = {}):
    self.settings = {
      'PROTOCOL': None,
      'MODULE': None,
      'PROTOCOL_ARGS': {
        'I2C_ADDRESS': None,
        'I2C_BUS_NUM': None,
        'STD_DELAY': None,
      },
      'COMMANDS': {
        'READ': {
          'CODE': None,
          'DELAY': None,
          'LENGTH': None,
          'UNIT': None,
        },
        'CAL': [{
          'CODE': None,
          'DELAY': None,
          'LENGTH': None,
        }]
      }
    }
    self.sensorName = sensorName
    if args.get('MODULE', None):
      self._handle_module(args['MODULE'])
    settings_update(self.settings, args)
    print(self.settings)
    self.prep_sensor()
    self.lastReading = { 'time': None, 'val': None }

  def get_setting(self, setting, default = None):
    if setting in self.settings:
      return self.settings.get(setting, default)
    else:
      return default

  def _handle_module(self, module, settings = None):
    if not settings:
      settings = self.settings
    presets = preset_sensor_modules.get(module, {})
    if presets.get('MODULE', None):
      self._handle_module(presets['MODULE'], presets)
    settings_update(settings, presets)
    settings['MODULE'] = module

  def prep_sensor(self):
    if self.settings.get('PROTOCOL', None) == 'I2C':
      self._i2c_prep_sensor()
    else:
      raise Exception(error_builder('Unknown protocol: ' + self.settings.get('PROTOCOL', None), self.sensorName, None))

  def _i2c_prep_sensor(self):
    args = self.settings.get('PROTOCOL_ARGS', {})
    args['READ_COMMAND'] = self.settings.get('COMMANDS', {}).get('READ', {})
    args['SENSOR_NAME'] = self.sensorName
    self.sensor = I2CDevice(args)

  def get_reading(self):
    if self.settings.get('PROTOCOL', None) == 'I2C':
      return self._i2c_get_reading()
    else:
      raise Exception(error_builder('Unknown protocol: ' + self.settings.get('PROTOCOL', None), self.sensorName, None))

  def _i2c_get_reading(self):
    cmd, delay = self._i2c_commands('READ')
    response = self.sensor.query(cmd, delay)
    if hasattr(readCommand, 'unit'):
      response.set_unit(readCommand['unit'])
    return response

  def _i2c_commands(self, commandName):
    if commandName in self.settings.get('COMMANDS', {}):
      cmd = self.settings.get('COMMANDS', {}).get(commandName, {}).get('CODE', '')
      delay = self.settings.get('COMMANDS', {}).get(commandName, {}).get('DELAY', None)
      delay = delay if delay else self.settings.get('STD_DELAY', None)
      return cmd, delay
    else:
      raise Exception(error_builder('Unknown command: ' + commandName, self.sensorName, None))

  def parallel_read(self):
    return self.sensor.parallel_read()

  def query(self, command, delay = None):
    if self.settings.get('PROTOCOL', None) == 'I2C':
      return self._i2c_query(command, delay)
    else:
      raise Exception(error_builder('Unknown protocol: ' + self.settings.get('PROTOCOL', 'Unknown', self.sensorName, None)))

  def _i2c_query(self, command, delay = None):
    if not delay or delay < 0:
      delay = self.settings.get('STD_DELAY', None)
    return self.sensor.query(command, delay)
