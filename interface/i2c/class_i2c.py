#!/usr/bin/python

from smbus2 import SMBus
from time import sleep
# import io
# import sys
# import fcntl
# import time
# import copy
# import string

class I2C:
  DEFAULT_BUS_NUM = 1
  DEFAULT_ADDRESS = 0x27

  def __init__(self, address=None, busNum=None):
    if not address:
      try:
        self.address = int('0x{}'.format(
                  findall("[0-9a-z]{2}(?!:)", check_output(['/usr/sbin/i2cdetect', '-y', str(BUS_NUMBER)]).decode())[0]), base=16) \
                  if exists('/usr/sbin/i2cdetect') else self.DEFAULT_ADDRESS
      except:
        self.address = self.DEFAULT_ADDRESS
    else:
      self.address = address
    self.busNum = busNum or self.DEFAULT_BUS_NUM
    self.bus = SMBus(self.busNum)

  def write_byte(self, cmd):
    self.bus.write_byte(self.address, cmd)

  def write_block_data(self, data):
    self.bus.write_block_data(self.address, 0, data)

  def write_string(self, string):
    self.write_block_data(self.string_to_bytes(string))

  def read_byte(self):
    return self.bus.read_byte(self.address)

  def read_block_data(self):
    return self.bus.read_i2c_block_data(self.address, 0, 32)

  def read_byte_data(self):
    return self.bus.read_byte_data(self.address, 0)

  def string_to_bytes(self, string):
    # output = bytes(string, 'ascii')
    output = string.encode('latin-1')
    return output

  def query_string(self, cmd, timeout=1, errorMsg=""):
    errorMsg += ": " if errorMsg else ""
    errorMsg += 'Error writing ' + cmd + ' to I2C device ' + str(self.address)
    try:
      # encoded = 'Find'.encode('latin-1')
      encoded = 'Find'.encode('latin-1')
      # encoded = 105
      print('Sending', encoded)
      # self.write_string(cmd)
      print(self.bus.write_i2c_block_data(self.address, 0, encoded))
    except Exception as e:
      # raise Exception(errorMsg + '\nException error: ' + repr(e) + '\n')
      return errorMsg + '\nException error: ' + repr(e) + '\n'
    except:
      # raise Exception(errorMsg + ': Other error')
      return errorMsg + ': Other error'
    else:
      sleep(timeout)
      print('successful write')
      try:
        print('read block data: ' + str(self.read_block_data()))
      except Exception as e:
        print('Exception error: ' + repr(e))
        return errorMsg + '\nException error: ' + repr(e) + '\n'
      try:
        print('read byte: ' + str(self.read_byte()))
      except Exception as e:
        print('Exception error: ' + repr(e))
        return errorMsg + '\nException error: ' + repr(e) + '\n'
      try:
        print('read byte data: ' + str(self.read_byte_data()))
      except Exception as e:
        print('Exception error: ' + repr(e))
        return errorMsg + '\nException error: ' + repr(e) + '\n'
      try:
        print('read word data: ' + str(self.bus.read_i2c_block_data(self.address, 0, 32)))
      except Exception as e:
        print('Exception error: ' + repr(e))
        return errorMsg + '\nException error: ' + repr(e) + '\n'
      else:
        return 'self.read_block_data()'
    finally:
      return 'End'
