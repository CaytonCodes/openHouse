#!/usr/bin/python
class DataOut:
  deviceName: str = None
  data: str = None
  unit: str = None
  statusCode: int = None
  responseType: str = None
  cmd: str = None

  def __init__(self, args):
    for k in args:
      setattr(self, k, args[k])

  def __str__(self):
    return str(self.__dict__)

  def set(self, key, value):
    setattr(self, key, value)

  def get(self, key, default = None):
    return getattr(self, key, default)

class Response:
  deviceName: str = None
  protocol: dict = {}
  inputCmd: str = None
  responseType: str = 'request'
  statusCode: int = None
  data: bytes = None
  unit: str = None

  def __init__(self, args):
    self.set_args(args)

  def set_args(self, args):
    for k in args:
      setattr(self, k, args[k])

  def recycle(self, args = None):
    self.data = None
    self.statusCode = None
    self.responseType = 'request'
    if args:
      self.set_args(args)
    return self

  def get_data(self):
    dataOut = {
      'deviceName': self.deviceName,
      'data': self.data,
      'statusCode': self.statusCode,
      'responseType': self.responseType,
      'unit': self.unit,
      'cmd': self.inputCmd
    }
    return DataOut(dataOut)

  def set_cmd(self, cmd, unit = None, delay = None):
    if unit:
      self.unit = unit
    self.inputCmd = cmd

  def get_cmd(self):
    return self.inputCmd

  def set_data(self, data, statusCode = 1, responseType = 'data'):
    self.data = data
    self.statusCode = statusCode
    self.responseType = responseType
    return self.data
