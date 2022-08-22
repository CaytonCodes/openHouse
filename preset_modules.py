#!/usr/bin/env python
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
      'ENCODING': 'latin-1',
      'NULL_CHAR': '\x00',
      'STD_DELAY': 1,
    },
    'BLANK_READING': '-',
    'ERROR_READINGS': [b'0.000', b''],
    'COMMANDS': {
      'READ': {
        'CODE': 'R',
        'DELAY': 0.9,
      },
    }
  }
}