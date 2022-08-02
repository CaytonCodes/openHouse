#!/usr/bin/env python

def settings_update(settings, args):
  if isinstance(args, dict):
    for key in args:
      if isinstance(args[key], dict):
        settings[key] = settings_update(settings[key] if key in settings else {}, args[key])
      elif args[key] is not None:
        settings[key] = args[key]
  return settings

def error_builder(msg: str, sensorName = '', error = None):
  if error:
    error = ': ' + error.__str__().encode('utf-8')
  else:
    error = ''
  return 'Error in ' + sensorName + ': ' + msg + error
