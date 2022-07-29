#!/usr/bin/python

import io
import fcntl
import time
import struct

DEFAULT_BUS_NUM = 1
DEFAULT_ADDRESS = 0x27
DEFAULT_TIMEOUT = 1
DEFAULT_NULL_CHAR = '\x00'
DEFAULT_ENCODING = 'latin-1'

class Response:
  sensorName: str
  sensorAddress: int
  inputCmd: str
  responseType: str
  statusCode: int
  data: bytes

  def get_data(self, default = b"", type = 'bytes', encoding = DEFAULT_ENCODING):
    if hasattr(self, 'data'):
      output =  self.data
    else:
      output = default
    if type == 'string':
      output = output.decode(encoding)
    if type == 'float':
      output = float(output)
    if type == 'int':
      output = round(float(output))
    return output

class I2CDevice:
  def __init__(self, address: int = DEFAULT_ADDRESS, busNum: int = DEFAULT_BUS_NUM, sensor_name: str = "", existingFile = None):
    self.busNum: int = busNum

    if existingFile:
      self.deviceFile = existingFile
    else:
      self.openFile()
    if address:
      self.setAddress(address)
    self.nullChar: str = DEFAULT_NULL_CHAR
    self.encoding: str = DEFAULT_ENCODING
    self.sensorName: str = sensor_name

  def openFile(self):
    self.deviceFile = io.open(file=f"/dev/i2c-{self.busNum}", mode="r+b", buffering=0)

  def setAddress(self, address: int):
    self.address: int = address
    fcntl.ioctl(self.deviceFile, 0x0703, self.address)

  def write(self, cmd: str):
    self.deviceFile.write((cmd + self.nullChar).encode(self.encoding))

  def _handle_response(self, inputCmd: str, dataBack):
    response = Response()
    response.sensorName = self.sensorName
    response.sensorAddress = self.address
    response.inputCmd = inputCmd
    if dataBack:
      response.data = dataBack[1:].strip().strip(bytes(self.nullChar, self.encoding))
      response.statusCode = int(dataBack[0])
      response.responseType = 'data'
    return response

  def _handle_error(self, errorMsg = '', e = None, response = None, inputCmd: str = '', dataBack = b""):
    print(e)
    if not response:
      response = self._handle_response(inputCmd, dataBack)
    response.statusCode = -1
    response.responseType = 'error'
    response.data = b"".join([response.get_data(), errorMsg.encode(self.encoding), e.__str__().encode(self.encoding)])
    response.error = e
    return response

  def read(self, inputCmd: str, byteCount: int = 31):
    readOut = self.deviceFile.read(byteCount)
    return self._handle_response(inputCmd, readOut)

  def query(self, cmd: str, timeout: int = DEFAULT_TIMEOUT):
    try:
      self.write(cmd)
    except Exception as e:
      errorMsg = f"Error writing {cmd} to I2C device at: {self.address} : "
      return self._handle_error(errorMsg, e, inputCmd=cmd)
    except:
      errorMsg = f"Unknown Error writing {cmd} to I2C device at: {self.address}"
      return self._handle_error(errorMsg, inputCmd=cmd)
    else:
      time.sleep(timeout)
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