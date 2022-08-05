import pytz
from datetime import datetime, timezone
from time import sleep
import yaml
import interface.class_interface as interface
from sensors.class_sensor_manager import SensorManager

class OpenGrow:
  def __init__(self):
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
        self.log(exc, 1, True)

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
    self.log = self.interface.log

  def prep_sensors(self):
    sensorDict = self.get_config(['SENSORS'], [])
    self.sensorManager = SensorManager(sensorDict)

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

  def read_sensor(self, sensorName, returnType = 'unitValue', default = None, responseObject = None):
    if not responseObject:
      responseObject = self.sensorManager.parallel_read(sensorName)
    if responseObject:
      if returnType == 'unitValue':
        return responseObject.get_unit_value()
      elif returnType == 'raw':
        return responseObject.get_data()
      elif returnType == 'float' or returnType == 'int':
        return responseObject.get_data(returnType)
      elif returnType == 'response':
        return responseObject
      else:
        return responseObject.get_data('str')
    else:
      return default

  def check_keyboard(self):
    response = self.interface.check_keyboard(True, False)
    if response:
      keyboardInput = response.get('val', None)
      return keyboardInput
    else:
      return None

  def check_keyboard_enter(self):
    keyEvent = False
    response = self.check_keyboard()
    if response or response == '':
      keyEvent = True
    return keyEvent

  def device_chat(self):
    exitChatString = '----EXITING CHAT MODE----\n'
    device = None
    deviceTypeOptions = ['SENSORS', 'DRIVERS']

    self.log('----ENTERING CHAT MODE----\nEnter exit or cntl + C to exit\n', 1, True)
    deviceType = self.interface.get_input('Which type of device?', deviceTypeOptions)
    if deviceType == 'exit':
      self.log(exitChatString, 2, True)
      return
    deviceOptions = self.get_config([deviceType, deviceType], [])
    deviceName = self.interface.get_input('Which device?', deviceOptions)
    if deviceName == 'exit':
      self.log(exitChatString, 2, True)
      return
    if deviceType == 'SENSORS':
      device = self.sensorManager.get_sensor(deviceName)
    elif deviceType == 'DRIVERS':
      # device = self.driverManager.get_driver(deviceName)
      self.log('drivers not yet implemented', 1, True)
    if not device:
      self.log('Device not found, try again.', 1, True)
      return self.device_chat()
    self.log('Prepare to enter chat type. CAL chat accepts commands then shows readings of sensor and only sends command when you press enter.', 2, True)
    chatType = self.interface.get_input('What is the chat type?', ['GENERAL', 'CAL'])
    chatPrompt = 'In cal chat, you will see readings and select when to send command.\n' if chatType == 'CAL' else ''
    chatPrompt += 'Enter a command to send to the device.'
    self.log('Entering chat mode. Type "exit" to exit.', 2, True)
    chatting = True
    while chatting:
      command = self.interface.get_input(chatPrompt)
      if command == 'exit':
        chatting = False
      else:
        if chatType == 'CAL':
          self.log('Reading sensor. Press enter to send command.', 1, True)
          waitingToSend = True
          while waitingToSend:
            sleep(1)
            reading = self.read_sensor(deviceName, 'unitValue')
            self.log('Reading: ' + reading, 0, True)
            if self.check_keyboard_enter():
              waitingToSend = False
        self.log('Sending command: ' + command + ' to device: ' + deviceName, 1, True)
        responseObject = self.sensorManager.sensor_query(deviceName, command)
        if responseObject:
          response = self.read_sensor(deviceName, 'response', b'', responseObject)
          self.log('Device Response: ' + response.get_data('str'), 2, True)
        else:
          self.log('Device Response: N/A', 2, True)
    self.log(exitChatString, 2, True)
    return


  def run(self):
    try:
      while True:
        self.log("Looping", 0, True)
        # self.log(manager.sensorManager.parallel_read('PH1').get_unit_value())
        if self.check_keyboard() == 'chat':
          self.device_chat()
        sleep(5)
    except KeyboardInterrupt:
        # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
        self.log("Cleaning up!", 1, True)
        # display.clear()