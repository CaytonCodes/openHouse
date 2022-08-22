#!/usr/bin/env python
from preset_modules import preset_modules

def _settings_update(settings, args):
  if isinstance(args, dict):
    if args.get('MODULE', None):
      _handle_module(settings, args['MODULE'])
    _settings_match(settings, args)
  return settings

def _settings_match(settings, args):
  for key in args:
    if isinstance(args[key], dict):
      settings[key] = _settings_match(settings[key] if key in settings else {}, args[key])
    elif args[key] is not None:
      settings[key] = args[key]
  return settings

def _handle_module(settings, module, subSettings = None):
  if subSettings:
    settings = subSettings
  # Get preset module dict.
  presets = preset_modules.get(module, {})
  # If preset is a module, handle it recursively.
  if presets.get('MODULE', None):
    _handle_module(settings, presets['MODULE'], presets)
  _settings_match(settings, presets)
  settings['MODULE'] = module

def _error_builder(msg: str, sensorName = '', error = None):
  if error:
    error = ': ' + error.__str__().encode('utf-8')
  else:
    error = ''
  return 'Error in ' + sensorName + ': ' + msg + error
