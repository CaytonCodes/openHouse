#!/usr/bin/env python

import pytz
from time import sleep
from datetime import datetime, timezone
from devices.class_device import SensorDevice
from _common_funcs import _settings_update, _error_builder
from comms.class_response import DataOut

STATS_LOOP_LIMIT = 1000

class SensorManager:
  def __init__(self, args = {}, comms = {}, timezone = 'UTC', _12hr = True):
    self.sensors = {}
    self.settings = {}
    _settings_update(self.settings, args)
    self.comms = comms
    self.prep_sensors()
    self.timezone = timezone
    self._12hr = _12hr

  def prep_sensors(self):
    inputSensors = self.settings.get('SENSORS', {})
    for sensorName in inputSensors:
      sensorSettings = inputSensors.get(sensorName, {})
      comm = self.get_comm(sensorSettings.get('PROTOCOL', None))
      instance = self.prep_sensor(sensorName, sensorSettings, comm)
      if instance:
        self.sensors[sensorName] = instance

  def _empty_data(self, sensorName = '', msg = ''):
    msg = msg if msg else 'No data'
    dataOb = { 'data': 'N/A', 'unit': '', 'sensor': sensorName, 'data': msg, 'responseType': 'error', 'statusCode': -1 }
    return DataOut(dataOb)

  def _simple_data(self, sensorName, data, unit = ''):
    dataOb = { 'data': data, 'unit': unit, 'sensor': sensorName, 'responseType': 'data', 'statusCode': 1 }
    return DataOut(dataOb)

  def set_timezone(self, timezone):
    self.timezone = timezone

  def get_current_time(self):
    output_format = ('%I:%M %p') if self._12hr else ('%H:%M')
    return datetime.now(timezone.utc).astimezone(pytz.timezone(self.timezone)).strftime(output_format)

  def wake_up(self):
    for sensorName in self.sensors:
      self.sensors[sensorName].wake_up()

  def go_to_sleep(self):
    for sensorName in self.sensors:
      self.sensors[sensorName].go_to_sleep()

  def get_comm(self, commName):
    return self.comms.get(commName, None)

  def prep_sensor(self, sensorName, sensorSettings, comm):
      return SensorDevice(sensorSettings, sensorName, 'SENSOR', comm)

  def get_sensor(self, sensorName):
    return self.sensors.get(sensorName, None)

  def get_sensors(self):
    return self.sensors

  def get_sensor_names(self):
    return self.sensors.keys()

  def sensor_query(self, sensorName, command, delay = None):
    return self.sensors[sensorName].query(command, delay)

  def read_sensor(self, sensorName, returnType = 'raw', default = None, responseData = None):
    if not responseData:
      responseData = self.parallel_read(sensorName)
    if responseData:
      if returnType == 'unitValue':
        return str(responseData.get('data', default)) + ' ' + responseData.get('unit', default)
      elif returnType == 'raw':
        return responseData
      elif returnType == 'float':
        return float(responseData.get('data', default))
      elif returnType == 'int':
        return round(float(responseData.get('data', default)))
      else:
        return str(responseData.get('data', default))
    else:
      return default

  def parallel_read(self, sensorName):
    if sensorName in self.sensors:
      try:
        output = self.sensors[sensorName].parallel_read()
        return output
      except Exception as e:
        error = _error_builder('SensorManager - parallel_read', sensorName, e)
        raise Exception(error)
        return error
    else:
      return self._empty_data(sensorName, 'Sensor not found')

  def parallel_read_all(self):
    readings = {}
    for sensorName in self.sensors:
      readings[sensorName] = self.parallel_read(sensorName)
    return readings

  def get_stats(self, statsDict):
    '''
    Returns a dictionary of the requested stats. Using the following format:
    { 'statName': { 'data': 'value', 'unit': 'unit' }, ... }
    '''
    output = {}
    readsLeft = len(statsDict)
    for i in range(STATS_LOOP_LIMIT):
      if readsLeft == 0:
        break
      for statName in statsDict:
        if statName not in output:
          reading = self.get_stat(statName, statsDict[statName])
          if reading:
            print('reading: ', str(reading))
            statData = {
              'data': reading.get('data', 'N/A'),
              'unit': reading.get('unit', ''),
            }
            output[statName] = statData
            readsLeft -= 1
      sleep(0.5)
    print('output:', str(output))
    return output

  def get_stat(self, statName, statDetails):
      statType = statDetails.get('TYPE', None)
      if statType == 'time':
        return self._simple_data('time', self.get_current_time(), '')
      elif statType == 'sensor' and statDetails.get('SENSOR', '') in self.get_sensor_names():
        return self.read_sensor(statName, 'raw', None)
      else:
        return self._empty_data(statName, 'Stat not found')