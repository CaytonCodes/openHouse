#!/usr/bin/env python
from struct import unpack

# Decode functions return a tuple of (decoded data, status code)

def ezo_decode(data: bytes) -> str:
  statusCode = int(data[0])
  data = data[1:].strip().strip(bytes('\x00', 'latin-1')).decode('latin-1')
  return data, statusCode

def ezo_encode(cmd: str) -> bytes:
  cmd += '\x00'
  return cmd.encode('latin-1')

def MCP9600_read(response, smbus):
  address = response.protocol_arg('I2C_ADDRESS')
  byteCount = response.protocol_arg('BUFFER_SIZE', 16)
  readOut = smbus.read_i2c_block_data(address, 0, 3)
  readOut = bytearray(readOut)
  return readOut

def MCP9600_decode(data: bytes) -> str:
  statusCode = 1
  print(data)
  # print(int.from_bytes(data, byteorder='big') / 16)
  value = unpack('>xH', data)[0] * 0.0625
  return value, statusCode


preset_modules = {
  'atlasSciEZOPH': {
    'MODULE': 'atlasSciEZO',
    'PROTOCOL_ARGS': {
      'I2C_ADDRESS': 0x63,
    },
    'COMMANDS': {
      'READ': {
        'UNIT': 'ph',
      },
    },
  },
  'atlasSciEZO': {
    'PROTOCOL': 'I2C',
    'PROTOCOL_ARGS': {
      'SUB_PROTOCOL': 'string',
      'STD_DELAY': 1,
      'ENCODE': ezo_encode,
      'DECODE': ezo_decode,
    },
    'BLANK_READING': '-',
    'ERROR_READINGS': ['0.000', ''],
    'COMMANDS': {
      'READ': {
        'CODE': 'R',
        'DELAY': 0.9,
      },
    }
  },
  'MCP9600': {
    'PROTOCOL': 'I2C',
    'PROTOCOL_ARGS': {
      'I2C_ADDRESS': 0x60,
      'STD_DELAY': 1,
      'BUFFER_SIZE': 16,
      'READ': MCP9600_read,
      'DECODE': MCP9600_decode,
    },
    'COMMANDS': {
      'READ': {
        'CODE': 0x00,
        'DELAY': 0.001,
        'UNIT': '°C',
      },
    }
  },
}