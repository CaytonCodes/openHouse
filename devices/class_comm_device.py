#!/usr/bin/env python

from time import sleep
from datetime import datetime
from _common_funcs import _settings_update, _error_builder
from comms.class_response import Response
from comms.class_i2c_manager import I2CManager

# All comm defaults
DEFAULT_DELAY = 0.1
DEFAULT_READING_REJECTION_AGE = 60
DEFAULT_MAX_READ_ATTEMPTS = 5

# I2C defaults
DEFAULT_I2C_ADDRESS = 0x27
DEFAULT_BUFFER_SIZE = 31

class CommDevice:
  '''
  A base class for all communication devices. Operates as a go between for devices and protocols of differing nature. Use appropriate subclass for device, either preset device subclass or general protocol subclass.
  '''
  def __init__(self, args, deviceName = '', commManager = None):
    self.settings = {
      'DELAY': DEFAULT_DELAY,
      'READING_REJECTION_AGE': DEFAULT_READING_REJECTION_AGE,
      'MAX_READ_ATTEMPTS': DEFAULT_MAX_READ_ATTEMPTS,
      'COMMANDS': {},
      'ERROR_READINGS': [],
      'BLANK_READING': '-',
      'UNIT' : '',
    }
    _settings_update(self.settings, args)
    self.commManager = commManager
    self.deviceName = deviceName
    self.lastReadCall = None
    self.noReadCount = 0
    self.response = self._prep_request()
    self.delay = self.settings.get('DELAY', DEFAULT_DELAY)
    self.readCmd = self.settings.get('COMMANDS', {}).get('READ', {}).get('CMD', '')
    self.readDelay = self.settings.get('COMMANDS', {}).get('READ', {}).get('DELAY', self.delay)

  def sub_settings_defaults(self, subDefualts):
    for setting in subDefualts:
      if setting not in self.settings.keys():
        self.settings[setting] = subDefualts[setting]

  def _prep_request(self):
    args = {
      'deviceName': self.deviceName,
      'unit': self.settings.get('UNIT', ''),
    }
    return Response(args)

  def _set_command(self, cmd):
    self.response.recycle()
    self.response.set_cmd(cmd)

  def command_out(self, cmd):
    '''
    Send command to device.
    @param cmd: command to send to device
    '''
    self.commManager.write(cmd)

  def get_reading(self):
    '''
    Get a reading from the device.
    @return: reading
    '''
    return self.commManager.read()

  def deviceWrite(self):
    '''
    Encode command and send to device.
    '''
    cmd = self.response.get_cmd()
    cmd = self.encode(cmd)
    # try this
    self.command_out(cmd)

  def deviceRead(self):
    '''
    Read data, decode, and set to response.
    '''
    # try this
    output = self.get_reading()

    output, statusCode = self.decode(output)
    self.response.set_data(output, statusCode, 'data')

  def encode(self, cmd):
    '''
    Encode command for sending to device.
    @param cmd: command to send to device
    @return: encoded command
    '''
    return cmd

  def decode(self, data):
    '''
    Decode data from device. Return decoded data and status code.
    @param data: data to decode
    @return: decoded data, status code
    '''
    statusCode = 1
    return data, statusCode

  def write(self, cmd):
    '''
    Set command in response and call to send to device.
    @param cmd: command to send to device
    '''
    self._set_command(cmd)
    self.deviceWrite()

  def read(self):
    '''
    Call to read from device, get response data output object, and error check.
    @return: data output from response object, error checked.
    '''
    self.deviceRead()
    dataOut = self.response.get_data()
    return self.error_check(dataOut)

  def query(self, cmd = None, delay = None):
    '''
    Send command to device, wait for delay period, and read response.
    @param cmd: command to send to device
    @param delay: delay between sending command and reading
    @return: data
    '''
    cmd, delay = self.cmd_delay_check(cmd, delay)
    self.write(cmd)
    sleep(delay)
    return self.read()

  def parallel_read(self, cmd = None, delay = None):
    '''
    Returns the latest reading from the device or False if reading not ready yet.
    Call until a reading is returned. Once a reading is found, the next one is called in the same run.
    @param cmd: command to send to device
    @param delay: delay between sending command and reading
    '''
    cmd, delay = self.cmd_delay_check(cmd, delay)
    dataOut = False
    timeNow = datetime.now()
    if self.lastReadCall and (timeNow - self.lastReadCall).total_seconds() < delay:
      # we haven't waited long enough since the last read call, let's get out of here.
      return self.parallel_read_counter(dataOut)
    if self.lastReadCall and (timeNow - self.lastReadCall).total_seconds() - delay < self.settings.get('READING_REJECTION_AGE', DEFAULT_READING_REJECTION_AGE):
      # only take reading if last call is less than our reading rejection age.
      dataOut = self.read()
    # Make new call, either we haven't made one yet, or we just took a reading, or we rejected the last reading.
    self.response.recycle()
    self.lastReadCall = timeNow
    # Check that we have the input command in our response still.
    if self.response.get_cmd() != cmd:
      self.write(cmd)
    else:
      self.deviceWrite()
    return self.parallel_read_counter(dataOut)

  def parallel_read_counter(self, dataOut):
    '''
    If no data, increment our noReadCount, if also over read attempt limit, set response as error reading.
    If reading is a blank reading, increment noReadCount.
    If reading is not a blank reading, reset noReadCount.
    @param dataOut: data output from device
    @return: dataOut
    '''
    # Handle no data
    if not dataOut:
      self.noReadCount += 1
      # Handle no data over read attempt limit
      if self.noReadCount > self.settings.get('MAX_READ_ATTEMPTS', DEFAULT_MAX_READ_ATTEMPTS):
        self.response.set_data(self.settings.get('BLANK_READING', '-'), 0, 'data')
        dataOut = self.response.get_data()
    # Handle blank reading
    elif dataOut.get('data') == self.settings.get('BLANK_READING', '-'):
      self.noReadCount += 1
    # Handle non-blank reading
    else:
      self.noReadCount = 0
    return dataOut

  def cmd_delay_check(self, cmd, delay):
    '''
    Check if command and delay arguments have been provided. If no command, default to device read command. If no delay, default to device delay.
    @param cmd: command to send to device
    @param delay: delay between sending command and reading
    @return: cmd, delay
    '''
    if not cmd:
      cmd = self.readCmd
      delay = self.readDelay if not delay else delay
    if not delay:
      delay = self.delay
    return cmd, delay

  def error_check(self, data):
    '''
    Check if the data is an error reading for this device. If so, modify to error reading.
    @param data: data to check
    @return: data
    '''
    if not data:
      return False
    if data.get('data', '') in self.settings.get('ERROR_READINGS', []):
      data['data'] = self.settings.get('BLANK_READING', '-')
    return data


class I2CDevice(CommDevice):
  def __init__(self, args, deviceName = '', commManager = None):
    super().__init__(args, deviceName, commManager)
    tempSettings = {
      'I2C_ADDRESS': DEFAULT_I2C_ADDRESS,
      'BUFFER_SIZE': DEFAULT_BUFFER_SIZE,
    }
    self.sub_settings_defaults(tempSettings)
    self.address = self.settings.get('I2C_ADDRESS', DEFAULT_I2C_ADDRESS)
    self.byteCount = self.settings.get('BUFFER_SIZE', DEFAULT_BUFFER_SIZE)
    if not self.commManager:
      self.commManager = I2CManager()

  def command_out(self, cmd):
    # if self.response.protocol_arg('SUB_PROTOCOL', '') == 'string':
    #   return self.commManager._write_io(self.address, cmd)
    return self.commManager.write_byte(self.address, cmd)

  def get_reading(self):
    # if self.response.protocol_arg('SUB_PROTOCOL', '') == 'string':
    #   self.commManager.setAddress(address)
    #   return self.commManager.ioFile.read(self.address, byteCount)
    return self.commManager.read_block(self.address, self.byteCount)