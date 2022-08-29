#!/usr/bin/env python

from devices.class_comm_device import CommDevice, I2CDevice
from devices.preset_modules import preset_modules
from _common_funcs import _settings_update

class Device:
  def __init__(self, args = {}, deviceName = '', deviceType = '', commManager = None):
    self.settings = {
      'PROTOCOL': None,
      'MODULE': None,
      'PROTOCOL_ARGS': {},
    }
    _settings_update(self.settings, args)
    self.protocol = self.settings.get('PROTOCOL', None)
    self.deviceName = deviceName
    self.deviceType = deviceType
    self._set_comm(commManager)

  def _set_comm(self, commManager = None):
    args = self.settings.get('PROTOCOL_ARGS', {})
    moduleName = self.settings.get('MODULE', None)
    if moduleName and moduleName in preset_modules.keys():
      self.comm = preset_modules.get(moduleName, CommDevice)(args, self.deviceName, commManager)
    elif self.protocol == 'I2C':
      self.comm = I2CDevice(args, self.deviceName, commManager)
    else:
      self.comm = CommDevice(args, self.deviceName, commManager)

  def write(self, cmd):
    return self.comm.write(cmd)

  def read(self):
    return self.comm.read()

  def query(self, command = None, delay = None):
    return self.comm.query(command, delay)

  def parallel_read(self, cmd = None, delay = None):
    return self.comm.parallel_read(cmd, delay)


class SensorDevice(Device):
  def __init__(self, args = {}, deviceName = '', deviceType = 'SENSOR', commManager = None):
    super().__init__(args, deviceName, deviceType, commManager)