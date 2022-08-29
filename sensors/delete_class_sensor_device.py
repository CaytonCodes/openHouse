#!/usr/bin/env python

from datetime import datetime
from _common_funcs import _settings_update, _error_builder
from comms.class_response import Response


DEFAULT_BUS_NUM = 1
DEFAULT_ADDRESS = 0x27
DEFAULT_DELAY = 1
DEFAULT_NULL_CHAR = ''
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
        },
      },
    }
    _settings_update(self.settings, args)
    self.sensorName = sensorName
    self.comm = comm
    self.protocol = self.settings.get('PROTOCOL', None)
    self.lastReadCall = None
    # self.prep_sensor()
    self.response = self._prep_request()


  # def prep_sensor(self):
  #   if self.settings.get('PROTOCOL', None) == 'I2C' and self.comm:
  #     pass
  #     # self._i2c_prep_sensor()
  #   else:
  #     raise Exception(error_builder('Unknown protocol: ' + self.settings.get('PROTOCOL', None) + ' with comm: ' + self.comm, self.sensorName, None))

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

  def parallel_read(self):
    cmd = self.settings.get('COMMANDS', {}).get('READ', {}).get('CODE', '')
    if self.response.inputCmd != cmd:
      self._set_command(cmd)
    dataOut = self.comm.parallel_read(self.response)
    return self.error_check(dataOut)

  def error_check(self, data):
    if not data:
      return False
    if data.get('data', '') in self.settings.get('ERROR_READINGS', []):
      data['data'] = self.settings.get('BLANK_READING', '-')
    return data

  def query(self, command, delay = None):
    self._set_command(command, delay)
    return self.comm.query(self.response)

