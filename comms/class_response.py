#!/usr/bin/python


class Response:
  deviceName: str = None
  protocol: dict = {}
  inputCmd: str = None
  responseType: str = 'request'
  statusCode: int = None
  data: bytes = None
  unit: str = None
  encoding: str = None

  def __init__(self, args):
    self.set_args(args)

  def recycle(self, args = None):
    self.data = None
    self.statusCode = None
    self.responseType = 'request'
    self.protocol_arg('LAST_READ_CALL', None, None)
    if args:
      self.set_args(args)
    return self

  def set_args(self, args):
    for k in args:
      setattr(self, k, args[k])

  def get_data(self):
    dataOut = { 'deviceName': self.deviceName, 'data': self.data, 'statusCode': self.statusCode, 'responseType': self.responseType, 'unit': self.unit }
    return dataOut

  def protocol_arg(self, arg, default = None, newVal = None):
    if newVal:
      self.protocol[arg] = newVal
    return self.protocol.get(arg, default)

  def set_cmd(self, cmd, unit = None, delay = None):
    self.unit = unit
    self.protocol_arg('TEMP_DELAY', None, delay)
    self.inputCmd = cmd

  def set_data(self, data, statusCode = 1, responseType = 'data'):
    self.data = data
    self.statusCode = statusCode
    self.responseType = responseType
    self.protocol_arg('TEMP_DELAY', None, None)
    return self.data

  # def get_data(self,  type = 'bytes', default = b"", encoding = None):
  #   encoding = encoding or self.encoding
  #   if hasattr(self, 'data'):
  #     output =  self.data
  #   else:
  #     output = default
  #   if self.responseType == 'error':
  #     return self.data
  #   if type == 'str':
  #     try:
  #       output = output.decode(encoding)
  #     except:
  #       return output
  #   if type == 'float':
  #     try:
  #       output = float(output)
  #     except:
  #       return output
  #   if type == 'int':
  #     try:
  #       output = round(float(output))
  #     except:
  #       return output
  #   return output

  # def get_unit_value(self, unit = None):
  #   if unit:
  #     self.set_unit(unit)
  #   if self.responseType == 'error':
  #     return self.data
  #   else:
  #     if hasattr(self.data, 'unit'):
  #       unit = ' ' + self.data.unit
  #     else:
  #       unit = ''
  #     return str(self.get_data(type = 'float')) + unit

  # def set_unit(self, unit):
  #   self.data.unit = unit
  #   return self