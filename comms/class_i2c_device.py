#!/usr/bin/python

import io
import fcntl
import time
import struct
import datetime
from _common_funcs import settings_update, error_builder

DEFAULT_BUS_NUM = 1
DEFAULT_ADDRESS = 0x27
DEFAULT_DELAY = 1000
DEFAULT_NULL_CHAR = '\x00'
DEFAULT_ENCODING = 'latin-1'
DEFAULT_BUFFER_SIZE = 31
DEFAULT_BLANK_READING = '-'

class Response:
  sensorName: str = None
  sensorAddress: int = None
  inputCmd: str = None
  responseType: str = None
  statusCode: int = None
  data: bytes = None
  unit: str = None

  def get_data(self, default = b"", type = 'bytes', encoding = DEFAULT_ENCODING):
    if hasattr(self, 'data'):
      output =  self.data
    if self.responseType == 'error':
      return self.data
    else:
      output = default
    if type == 'str':
      output = output.decode(encoding)
    if type == 'float':
      output = float(output)
    if type == 'int':
      output = round(float(output))
    return output

  def get_unit_value(self, unit = None):
    if unit:
      self.data.unit = unit
    if self.responseType == 'error':
      return self.data
    else:
      if hasattr(self.data, 'unit'):
        unit = ' ' + self.data.unit
      else:
        unit = ''
      return self.get_data(type = 'float') + unit

  def set_unit(self, unit):
    self.data.unit = unit
    return self

class I2CDevice:
  def __init__(self, args, existingFile = None, ):
    self.settings = {
      'SENSOR_NAME': '',
      'I2C_ADDRESS': DEFAULT_ADDRESS,
      'I2C_BUS_NUM': DEFAULT_BUS_NUM,
      'STD_DELAY': DEFAULT_DELAY,
      'NULL_CHAR': DEFAULT_NULL_CHAR,
      'ENCODING': DEFAULT_ENCODING,
      'BLANK_READING': DEFAULT_BLANK_READING,
      'ERROR_READINGS': [],
      'READ_COMMAND': {'CODE': '', 'DELAY': DEFAULT_DELAY, 'LENGTH': DEFAULT_BUFFER_SIZE, 'UNIT': ''},
    }

    settings_update(self.settings, args)

    if existingFile:
      self.deviceFile = existingFile
    else:
      self.openFile()
    self.setAddress(self.settings['I2C_ADDRESS'])
    self.lastReading = {'time': None, 'response': None}

  def openFile(self):
    self.deviceFile = io.open(file=f"/dev/i2c-{self.get_setting('I2C_BUS_NUM')}", mode="r+b", buffering=0)

  def get_setting(self, setting: str, default = None):
    if setting in self.settings:
      return self.settings[setting]
    else:
      return default

  def setAddress(self, address: int):
    self.address: int = address
    fcntl.ioctl(self.deviceFile, 0x0703, self.address)

  def write(self, cmd: str):
    self.deviceFile.write((cmd + self.settings['NULL_CHAR']).encode(self.settings['ENCODING']))

  def _handle_response(self, inputCmd: str, dataBack):
    response = Response()
    response.sensorName = self.settings['SENSOR_NAME']
    response.sensorAddress = self.settings['I2C_ADDRESS']
    response.inputCmd = inputCmd
    if inputCmd == self.settings['READ_COMMAND']['CODE']:
      response.unit = self.settings['READ_COMMAND']['UNIT']
    if dataBack:
      response.data = dataBack[1:].strip().strip(bytes(self.settings['NULL_CHAR'], self.settings['ENCODING']))
      response.statusCode = int(dataBack[0])
      response.responseType = 'data'
    if response.data in self.settings['ERROR_READINGS']:
      response = self._error_reading(response)
    return response

  def _error_reading(self, response):
    response.responseType = 'error'
    response.data = self.settings['BLANK_READING']
    return response

  def _handle_error(self, errorMsg = '', e = None, response = None, inputCmd: str = '', dataBack = b""):
    print(e)
    if not response:
      response = self._handle_response(inputCmd, dataBack)
    response.statusCode = -1
    response.responseType = 'error'
    response.data = b"".join([response.get_data(), errorMsg.encode(self.settings['ENCODING']), e.__str__().encode(self.settings['ENCODING'])])
    response.error = e
    return response

  def read(self, inputCmd: str, byteCount: int = 31):
    readOut = self.deviceFile.read(byteCount)
    return self._handle_response(inputCmd, readOut)

  def parallel_read(self):
    timeNow = datetime.datetime.now()
    if self.lastReading['time'] and (timeNow - self.lastReading['time']).total_seconds() * 1000 < self.settings['STD_DELAY']:
      # it's too soon to read again, return last read value
      return self.lastReading['response']
    else:
      self.lastReading['time'] = timeNow
      response = self.read(self.settings['READ_COMMAND']['CODE'])
      self.lastReading['response'] = response
      self.write(self.settings['READ_COMMAND']['CODE'])
      return response

  def query(self, cmd: str, delay: int = DEFAULT_DELAY):
    try:
      self.write(cmd)
    except Exception as e:
      errorMsg = f"Error writing {cmd} to I2C device at: {self.address} : "
      return self._handle_error(errorMsg, e, inputCmd=cmd)
    except:
      errorMsg = f"Unknown Error writing {cmd} to I2C device at: {self.address}"
      return self._handle_error(errorMsg, inputCmd=cmd)
    else:
      time.sleep(delay)
      try:
        readOut = self.read(cmd)
      except Exception as e:
        errorMsg = f"Error reading {cmd} response on I2C device at: {self.address}"
        return self._handle_error(errorMsg, e, inputCmd=cmd)
      except:
        errorMsg = f"Unknown Error reading {cmd} response on I2C device at: {self.address}"
        return self._handle_error(errorMsg, e, inputCmd=cmd)
      else:
        return readOut


  def close(self):
    self.deviceFile.close()