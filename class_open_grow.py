
from datetime import datetime
from time import sleep
import yaml
from comms.class_i2c_manager import I2CManager
import interface.class_interface as interface
from sensors.class_sensor_manager import SensorManager
from _common_funcs import _settings_update

class OpenGrow:
  def __init__(self):
    self.settings = {
      'GENERAL': {
        'TIMEZONE': 'UTC',
        '12_HOUR_CLOCK': True,
        'AWAKE_PERIOD': 60,
        'SLEEP_PERIOD': 60,
        'STATS_LOOP_LIMIT': 1000,
        'STATS': {
          'TIME': { 'type': 'time'},
        },
      },
      'SENSORS': {},
      'COMMS': {},
      'INTERFACE': {},
      'DRIVERS': {},
    }
    self.comms = {}
    self.build_config()
    _settings_update(self.settings, self.config)
    print(self.settings)
    self.prep_components()

  def prep_components(self):
    self.prep_comms()
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

  def prep_comms(self):
    args = self.config.get('COMMS', {})
    if args.get('I2C', False):
      protocol_args = args.get('I2C_ARGS', {})
      self.comms['I2C'] = I2CManager(protocol_args)

  def prep_interface(self):
    self.interface = interface.InterfaceManager(self.get_config(['INTERFACE']), self.comms.get('I2C', None))
    self.log = self.interface.log

  def prep_sensors(self):
    timezone = self.get_config(['GENERAL', 'TIMEZONE'], 'UTC')
    _12hr = self.get_config(['GENERAL', '12_HOUR_CLOCK'], True)
    sensorDict = self.get_config(['SENSORS'], [])
    self.sensorManager = SensorManager(sensorDict, self.comms, timezone, _12hr)

  def stats_screen(self):
    statsDict = self.settings.get('GENERAL', {}).get('STATS', {})
    stats_with_vals = self.sensorManager.get_stats(statsDict)
    self.interface.stats_log(stats_with_vals, True)

  def check_keyboard(self, enter = False):
    response = self.interface.check_keyboard(True, False)
    if enter:
      return ( response or response == '' )
    if response:
      keyboardInput = response.get('val', None)
      return keyboardInput
    else:
      return None

  # def check_keyboard_enter(self):
  #   response = self.check_keyboard()
  #   return ( response or response == '' )

  def device_chat(self):
    exitChatString = '----EXITING CHAT MODE----\n'
    device = None
    deviceTypeOptions = ['SENSORS', 'DRIVERS']

    self.log('----ENTERING CHAT MODE----\nEnter exit or cntl + C to exit\n', 1, True, True)
    deviceType = self.interface.get_input('Which type of device?', deviceTypeOptions)
    if deviceType == 'exit':
      self.log(exitChatString, 2, True, True)
      return
    deviceOptions = self.get_config([deviceType, deviceType], [])
    deviceName = self.interface.get_input('Which device?', deviceOptions)
    if deviceName == 'exit':
      self.log(exitChatString, 2, True, True)
      return
    if deviceType == 'SENSORS':
      device = self.sensorManager.get_sensor(deviceName)
    elif deviceType == 'DRIVERS':
      # device = self.driverManager.get_driver(deviceName)
      self.log('drivers not yet implemented', 1, True, True)
    if not device:
      self.log('Device not found, try again.', 1, True, True)
      return self.device_chat()
    self.log('Prepare to enter chat type. CAL chat accepts commands then shows readings of sensor and only sends command when you press enter.', 2, True, True)
    chatType = self.interface.get_input('What is the chat type?', ['GENERAL', 'CAL'])
    chatPrompt = 'In cal chat, you will see readings and select when to send command.\n' if chatType == 'CAL' else ''
    chatPrompt += 'Enter a command to send to the device.'
    self.log('Entering chat mode. Type "exit" to exit.', 2, True, True)
    chatting = True
    while chatting:
      command = self.interface.get_input(chatPrompt)
      if command == 'exit':
        chatting = False
      else:
        if chatType == 'CAL':
          self.log('Reading sensor. Press enter to send command.', 1, True, True)
          waitingToSend = True
          while waitingToSend:
            sleep(1)
            reading = self.read_sensor(deviceName, 'unitValue')
            if reading:
              self.log('Reading: ' + reading, 0, True, True)
            if self.check_keyboard(True):
              waitingToSend = False
        self.log('Sending command: ' + command + ' to device: ' + deviceName, 1, True, True)
        responseData = self.sensorManager.sensor_query(deviceName, command)
        if responseData:
          response = self.read_sensor(deviceName, 'raw', b'', responseData)
          self.log('Device Response: ' + str(response), 2, True, True)
        else:
          self.log('Device Response: N/A', 2, True, True)
    self.log(exitChatString, 2, True, True)
    return


  def run(self):
    try:
      while True:
        # self.log("Looping", 1, True)
        # print(self.sensorManager.parallel_read_all())
        self.stats_screen()
        sleep(1)

        keyboardCheck = self.check_keyboard()
        if keyboardCheck:
          if not self.log(None, 2, False):
            self.log('Keyboard input: ' + keyboardCheck, 1, True, True)
        if keyboardCheck == 'chat':
          self.device_chat()
    except KeyboardInterrupt:
        # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
        self.log("Cleaning up!", 1, True, True)
        self.interface.lcd_clear()