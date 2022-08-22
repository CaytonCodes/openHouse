#!/usr/bin/env python

from sensors.class_sensor_device import SensorDevice
from _common_funcs import _settings_update, _error_builder

class SensorManager:
  def __init__(self, args):
    self.sensors = {}
    self.settings = {
      'I2C_BUS_NUM': None,
    }
    _settings_update(self.settings, args)
    self.prep_sensors()

  def prep_sensors(self):
    sensors = self.settings.get('SENSORS', {})
    for sensorName in sensors:
      sensorSettings = sensors.get(sensorName, {})
      if self.settings.get('I2C_BUS_NUM', None) and sensorSettings.get('PROTOCOL', None) == 'I2C':
        if not sensorSettings.get('PROTOCOL_ARGS', {}):
          sensorSettings['PROTOCOL_ARGS'] = {}
        sensorSettings['PROTOCOL_ARGS']['I2C_BUS_NUM'] = self.settings.get('I2C_BUS_NUM', None)
      instance = self.prep_sensor(sensorName, sensorSettings)
      print('Sensor ' + sensorName + ' prepared.', instance)
      if instance:
        self.sensors[sensorName] = instance

  def prep_sensor(self, sensorName, sensorSettings):
      return SensorDevice(sensorName, sensorSettings)

  def get_sensor(self, sensorName):
    return self.sensors.get(sensorName, None)

  def get_sensors(self):
    return self.sensors

  def get_sensor_names(self):
    return self.sensors.keys()

  def read_sensor(self, sensorName):
    return self.sensors[sensorName].get_reading()

  def read_sensors(self):
    readings = {}
    for sensorName in self.sensors:
      readings[sensorName] = self.read_sensor(sensorName)
    return readings

  def sensor_query(self, sensorName, command, delay = None):
    return self.sensors[sensorName].query(command, delay)

  def parallel_read(self, sensorName):
    try:
      response = self.sensors[sensorName].parallel_read()
      return response
    except Exception as e:
      print(error_builder('Error in parallel read for sensor: ' + sensorName, e), sensorName, e)
      return None

  def parallel_read_all(self):
    readings = {}
    for sensorName in self.sensors:
      readings[sensorName] = self.parallel_read(sensorName)
    return readings


  def sensor_chat(self, sensorName, outputFunction = lambda x: print(x)):
    print('Sensor chat for ' + sensorName)
    # raw_input = vars(__builtins__).get('raw_input', input)
    try:
      while True:
        readingResponse = self.read_sensor(sensorName)
        readingUnitVal = readingResponse.get_unit_value()
        outputFunction(sensorName + ': ' + reading)
        command = raw_input('>> Enter command: ')
        if command:
          outputFunction('Sending Command: ' + command)
          # response = self.sensor_query(sensorName, command)
          # outputFunction('Response: ' + response.get_data(type = 'str'))
        time.sleep(1)
    except KeyboardInterrupt:
      print('\nEnding Chat.')
      return
