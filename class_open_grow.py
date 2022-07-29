import pytz
from datetime import datetime, timezone
import yaml
import interface.class_interface as interface
import comms.class_i2c_device as I2CDevice

class OpenGrow:
  def __init__(self):
    self.sensors = {}
    self.build_config()
    self.prep_components()

  def prep_components(self):
    if self.get_config('INTERFACE'):
      self.prep_interface()
    self.prep_sensors()

  def build_config(self):
    self.config = self.read_yaml('./config.yaml')
    return self.config

  def read_yaml(self, file_path):
    with open(file_path, 'r') as stream:
      try:
        return yaml.safe_load(stream)
      except yaml.YAMLError as exc:
        print(exc)

  def get_config(self, key = None, default = None):
    if type(key) is list:
        found = self.config
        for k in key:
          if type(found) is dict and k in found:
            found = found[k]
          else:
            found = None
            break
    elif key:
      found = self.config[key]
    else:
      found = self.config
    found = default if found is None else found
    return found

  def prep_interface(self):
    self.interface = interface.InterfaceManager(self.get_config(['INTERFACE']))

  def prep_sensors(self):
    sensorDict = self.get_config(['SENSORS', 'SENSORS'], [])
    self.i2cBus = self.get_config(['SENSORS', 'I2C_BUS'], 1)
    for sensor in sensorDict:
      instance = self.prep_sensor(sensorDict[sensor], sensor)
      if instance:
        self.sensors[sensor] = instance

  def prep_sensor(self, sensor, sensorName):
    sensorType = sensor['TYPE']
    if sensorType == 'I2C':
      instance = self.prep_i2c_sensor(sensor, sensorName)
    else:
      instance = None
    return instance

  def prep_i2c_sensor(self, sensor, sensorName):
    address = sensor['I2C_ADDRESS'] or None
    instance = I2CDevice.I2CDevice(address, self.i2cBus, sensorName)
    return instance

  def stats_screen(self):
    stats_list = self.get_config(['STATS', 'STATS_SCREEN'], ['TIME'])
    stats_with_vals = []
    for stat in stats_list:
      stats_with_vals.append([stat, self.get_stat(stat)])
    self.interface.stats_screen(stats_with_vals)

  def get_current_time(self):
    output_format = ('%I:%M %p') if self.get_config(['GENERAL', '12_HOUR_CLOCK']) else ('%H:%M')
    return datetime.now(timezone.utc).astimezone(pytz.timezone(self.get_config(['GENERAL', 'TIMEZONE']) or 'UTC')).strftime(output_format)

  def get_stat(self, stat):
    stat_details = self.get_config(['STATS', 'STATS', stat], {'TYPE': None})
    stat_type = stat_details['TYPE']
    if stat_type == 'time':
      return self.get_current_time()
    elif stat_type == 'temp':
      return '75.0 F'
    else:
      return 'N/A'
