#!/usr/bin/python


class Response:
  sensorName: str = None
  sensorAddress: int = None
  inputCmd: str = None
  responseType: str = None
  statusCode: int = None
  data: bytes = None
  unit: str = None
  encoding: str = 'utf-8'

  def __init__(self, args):
    for k in args:
      setattr(self, k, args[k])

  def set_data(self, data, statusCode = 1, responseType = 'data'):
    self.data = data
    self.statusCode = statusCode
    self.responseType = responseType
    return self.data

  def get_data(self,  type = 'bytes', default = b"", encoding = None):
    encoding = encoding or self.encoding
    if hasattr(self, 'data'):
      output =  self.data
    else:
      output = default
    if self.responseType == 'error':
      return self.data
    if type == 'str':
      try:
        output = output.decode(encoding)
      except:
        return output
    if type == 'float':
      try:
        output = float(output)
      except:
        return output
    if type == 'int':
      try:
        output = round(float(output))
      except:
        return output
    return output

  def get_unit_value(self, unit = None):
    if unit:
      self.set_unit(unit)
    if self.responseType == 'error':
      return self.data
    else:
      if hasattr(self.data, 'unit'):
        unit = ' ' + self.data.unit
      else:
        unit = ''
      return str(self.get_data(type = 'float')) + unit

  def set_unit(self, unit):
    self.data.unit = unit
    return self