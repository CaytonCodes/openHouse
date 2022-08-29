#!/usr/bin/python

import io
from smbus import SMBus
import fcntl
from time import sleep
import struct
from datetime import datetime
from _common_funcs import _settings_update, _error_builder

DEFAULT_DELAY = 1
DEFAULT_READING_REJECTION_AGE = 60
DEFAULT_BUFFER_SIZE = 31
PERIPHERAL_ADDRESS_CHANGE = 0x0703

class I2CManager:
  def __init__(self, args = {}, existingFile = None, existingBus = None):
    self.settings = {
      'I2C_BUS_NUM': 1,
      'STD_DELAY': DEFAULT_DELAY,
      'READING_REJECTION_AGE': DEFAULT_READING_REJECTION_AGE,
      'BUFFER_SIZE': DEFAULT_BUFFER_SIZE,
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

  def setAddress(self, address: int):
    self.address: int = address
    # this sets the peripheral address in the io file.
    fcntl.ioctl(self.ioFile, PERIPHERAL_ADDRESS_CHANGE, self.address)

  def write_io(self, address, cmd):
    self.setAddress(address)
    self.ioFile.write(cmd)

  def write_byte(self, address, data):
    self.bus.write_byte(address, data)
    sleep(0.01)

  def read_block(address, byteCount):
    return self.bus.read_i2c_block_data(address, 0, byteCount)

  def read_io(self, address, byteCount):
    self.setAddress(address)
    return self.ioFile.read(byteCount)

  def close(self):
    self.ioFile.close()
