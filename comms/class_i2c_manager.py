#!/usr/bin/python

import io
from smbus import SMBus
import fcntl
from time import sleep
import struct
from datetime import datetime
from _common_funcs import _settings_update, _error_builder

# DEFAULT_BUS_NUM = 1
# DEFAULT_ADDRESS = 0x27
DEFAULT_DELAY = 1
DEFAULT_READING_REJECTION_AGE = 60
# DEFAULT_NULL_CHAR = '\x00'
# DEFAULT_ENCODING = 'latin-1'
# DEFAULT_BUFFER_SIZE = 31
# DEFAULT_BLANK_READING = '-'
PERIPHERAL_ADDRESS_CHANGE = 0x0703

class I2CManager:
  def __init__(self, args, existingFile = None, existingBus = None):
    self.settings = {
      # 'DEVICE_NAME': '',
      # 'I2C_ADDRESS': DEFAULT_ADDRESS,
      'I2C_BUS_NUM': 1,
      'STD_DELAY': DEFAULT_DELAY,
      'READING_REJECTION_AGE': DEFAULT_READING_REJECTION_AGE,
      # 'NULL_CHAR': DEFAULT_NULL_CHAR,
      # 'ENCODING': DEFAULT_ENCODING,
      # 'BLANK_READING': DEFAULT_BLANK_READING,
      # 'ERROR_READINGS': [],
      # 'READ_COMMAND': {'CODE': '', 'DELAY': DEFAULT_DELAY, 'LENGTH': DEFAULT_BUFFER_SIZE, 'UNIT': ''},
    }

    _settings_update(self.settings, args)

    if existingFile:
      self.ioFile = existingFile
    else:
      self.ioFile = io.open(file=f"/dev/i2c-{self.settings.get('I2C_BUS_NUM', 1)}", mode="r+b", buffering=0)
    if existingBus:
      self.bus = existingBus
    else:
      self.bus = SMBus(self.settings['I2C_BUS_NUM'])
    # self.setAddress(self.settings['I2C_ADDRESS'])
    # self.lastReading = {'time': None, 'response': None}

  # def openFile(self):
  #   self.ioFile = io.open(file=f"/dev/i2c-{self.get_setting('I2C_BUS_NUM')}", mode="r+b", buffering=0)

  # def get_setting(self, setting: str, default = None):
  #   if setting in self.settings:
  #     return self.settings[setting]
  #   else:
  #     return default

  def setAddress(self, address: int):
    self.address: int = address
    # this sets the peripheral address in the io file.
    fcntl.ioctl(self.ioFile, PERIPHERAL_ADDRESS_CHANGE, self.address)

  def write(self, response): # address, cmd, encoding = None, nullChar = None):
    cmd = response.inputCmd
    address = response.protocol_arg('I2C_ADDRESS')
    encoding = response.protocol_arg('ENCODING')
    cmd += response.protocol_arg('NULL_CHAR', '')
    if encoding in ['bytes', 'byte', 'hex', 'hexadecimal', None]:
      return self.write_byte(address, cmd)
    cmd = cmd.encode(encoding)
    self._write_io(address, cmd)

  def _write_io(self, address, cmd):
    self.setAddress(address)
    self.ioFile.write(cmd)

  def write_byte(self, address, data):
    self.bus.write_byte(address, data)
    # data = bytes(data,)
    # self.ioFile.write(data)
    sleep(0.01)


  def _handle_response(self, response, dataBack):
    # args = {
    #   'deviceName': self.settings['DEVICE_NAME'],
    #   'protocol': {'type': 'I2C' , 'address': self.settings['I2C_ADDRESS']},
    #   'inputCmd': inputCmd,
    # }
    # if inputCmd == self.settings['READ_COMMAND']['CODE']:
    #   args['unit'] = self.settings['READ_COMMAND']['UNIT']
    # response = Response(args)

    # Moving this logic into read to not be so repetitive.
    data = None
    nullChar = response.protocol_arg('NULL_CHAR', '')
    encoding = response.protocol_arg('ENCODING', None)
    if dataBack:
      if encoding in ['bytes', 'byte', 'hex', 'hexadecimal', None]:
        data = dataBack
      else:
        statusCode = int(dataBack[0])
        data = dataBack[1:].strip().strip(bytes(nullChar, encoding))
      response.set_data(data, statusCode, 'data')
    if not data or data in response.protocol_arg('ERROR_READINGS', []):
      response = self._error_reading(response)
    return response

  def _error_reading(self, response):
    response.set_data(self.settings['BLANK_READING'], -1, 'error')
    return response

  # def _handle_error(self, errorMsg = '', e = None, response = None, inputCmd: str = '', dataBack = b""):
  #   if not response:
  #     response = self._handle_response(inputCmd, dataBack)
  #   errorData = b"".join([response.get_data(), errorMsg.encode(self.settings['ENCODING']), e.__str__().encode(self.settings['ENCODING'])])
  #   response.set_data(errorData, -1, 'error')
  #   response.error = e
  #   return response

  def read(self, response): # address, inputCmd: str, byteCount: int = 31):
    address = response.protocol_arg('I2C_ADDRESS')
    encoding = response.protocol_arg('ENCODING', None)
    if encoding not in ['bytes', 'byte', 'hex', 'hexadecimal', None]:
      self.setAddress(address)
      readOut = self.ioFile.read(byteCount)
    return self._handle_response(response, readOut)

  def get_delay(self, response):
    # delay order of use: response protocol args TEMP_DELAY, response protocol args STD_DELAY, settings STD_DELAY
    return response.protocol_arg('TEMP_DELAY', response.protocol_arg('STD_DELAY', self.settings.get('STD_DELAY', DEFAULT_DELAY)))

  def parallel_read(self, response):
    dataOut = False
    timeNow = datetime.now()
    lastReadCall = response.protocol_arg('LAST_READ_CALL', None)
    delay = self.get_delay(response)
    if lastReadCall and (timeNow - lastReadCall).total_seconds() < delay:
      # we haven't waited long enough since the last read call.
      return dataOut
    if lastReadCall and (timeNow - lastReadCall).total_seconds() - delay < self.settings.get('READING_REJECTION_AGE', DEFAULT_READING_REJECTION_AGE):
      # only take reading if last call is less than our reading rejection age.
      response = self.read(response)
      dataOut = response.get_data()
    response.recycle()
    response.protocol_arg('LAST_READ_CALL', timeNow)
    self.write(response)
    return dataOut


  # def parallel_read(self):
  #   timeNow = datetime.datetime.now()
  #   if self.lastReading['time'] and (timeNow - self.lastReading['time']).total_seconds() < self.settings['STD_DELAY']:
  #     # it's too soon to read again, return last read value
  #     return self.lastReading['response']
  #   else:
  #     print('new parallel reading for : ' + self.settings['DEVICE_NAME'])
  #     self.lastReading['time'] = timeNow
  #     response = self.read(self.settings['READ_COMMAND']['CODE'])
  #     self.lastReading['response'] = response
  #     self.write(self.settings['READ_COMMAND']['CODE'])
  #     return response

  def query(self, response):
    delay = self.get_delay(response)
    self.write(response)
    sleep(delay)
    return self.read(response)

  # def query(self, address, cmd, delay = None,  encoding = None, nullChar = None):
  #   if not delay:
  #     delay = DEFAULT_DELAY
  #   try:
  #     self.write(address, cmd, encoding, nullChar)
  #   except Exception as e:
  #     errorMsg = f"Error writing {cmd} to I2C device at: {self.address} : "
  #     return self._handle_error(errorMsg, e, inputCmd=cmd)
  #   except:
  #     errorMsg = f"Unknown Error writing {cmd} to I2C device at: {self.address}"
  #     return self._handle_error(errorMsg, inputCmd=cmd)
  #   else:
  #     sleep(delay)
  #     try:
  #       readOut = self.read(address, cmd)
  #     except Exception as e:
  #       errorMsg = f"Error reading {cmd} response on I2C device at: {self.address}"
  #       return self._handle_error(errorMsg, e, inputCmd=cmd)
  #     except:
  #       errorMsg = f"Unknown Error reading {cmd} response on I2C device at: {self.address}"
  #       return self._handle_error(errorMsg, e, inputCmd=cmd)
  #     else:
  #       return readOut

  def close(self):
    self.ioFile.close()