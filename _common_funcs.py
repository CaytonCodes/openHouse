#!/usr/bin/env python

def _settings_update(settings, args):
  if isinstance(args, dict):
    _settings_match(settings, args)
  return settings

def _settings_match(settings, args):
  for key in args:
    if isinstance(args[key], dict):
      settings[key] = _settings_match(settings[key] if key in settings else {}, args[key])
    elif args[key] is not None:
      settings[key] = args[key]
  return settings

def _error_builder(msg: str, sensorName = '', error = None):
  if error:
    error = ': ' + error.__str__()
  else:
    error = ''
  return 'Error in ' + sensorName + ': ' + msg + error
