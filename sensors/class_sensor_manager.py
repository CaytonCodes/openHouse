#!/usr/bin/env python

from devices.class_device import SensorDevice
from _common_funcs import _settings_update, _error_builder

class SensorManager:
  def __init__(self, args, comms, log = None):
    self.sensors = {}
    self.settings = {}
    _settings_update(self.settings, args)
    self.comms = comms
    self.log = log if log else lambda x, y = None, z = None, a = None: print(x)
    self.prep_sensors()

  def prep_sensors(self):
    sensors = self.settings.get('SENSORS', {})
    for sensorName in sensors:
      sensorSettings = sensors.get(sensorName, {})
      comm = self.get_comm(sensorSettings.get('PROTOCOL', None))
      instance = self.prep_sensor(sensorName, sensorSettings, comm)
      print('Sensor ' + sensorName + ' prepared.', instance)
      if instance:
        self.sensors[sensorName] = instance

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
      output = self.sensors[sensorName].parallel_read()
      return output
    except Exception as e:
      self.log(_error_builder('Error in parallel read.', sensorName, e), 0, True)
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
