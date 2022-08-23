from time import sleep
import interface.lcd.class_lcd_manager as lcd_manager
from interface.inputs.class_keyboard_watcher import KeyboardWatcher

class InterfaceManager:
  def __init__(self, config, comm):
    self.config = config
    self.comm = comm
    self.prep_components()

  def prep_components(self):
    if self.config.get('LCD', None):
      self.prep_display()
    self.keyboard = KeyboardWatcher()

  def prep_display(self):
    args = self.config.get('LCD', {})
    self.display = lcd_manager.LcdManager(args, self.comm)

  def check_keyboard(self, complete = True, log = False):
    '''When complete is true, will return the response only after the breaker is hit. Otherwise will return response with running string. Response: {'val': '', 'complete': False}.'''
    response = self.keyboard.get_running_string()
    if complete:
      if not response.get('complete', False):
        response = False
    if log and response:
      self.log('keyboard response: ' + response.get('val', None) + ': complete' if response.get('complete', None) else ': incomplete')
    return response

  def get_input(self, prompt = '', options = [], default = None):
    if options and not prompt.startswith('Invalid input.'):
      prompt = 'Options: ' + ', '.join(options) + '\n' + prompt
    try:
      inputVal = self._input(prompt + ' ')
    except KeyboardInterrupt:
      return 'exit'
    except:
      inputVal = 'except'
    self.log('--input recieved: ' + inputVal, 0, True)
    if inputVal == 'exit':
      return 'exit'
    if options:
      if inputVal in options:
        return inputVal
      elif default:
        return default
      else:
        return self.get_input('Invalid input. ' + prompt, options, default)
    else:
      return inputVal

  def _input(self, prompt = ''):
    prompt = '\n' + prompt if prompt else ''
    self.log(prompt, 0, True)
    waiting = True
    while waiting:
      response = self.check_keyboard()
      if response:
        waiting = False
      sleep(0.5)
    return response.get('val', None)

  def log(self, message, delay = 0, forcePrint = False, skipDisplay = False):
    isComplete = True
    if type(message) != str:
      message = str(message)
    toPrint = True if forcePrint or not self.display else False
    if self.display and not skipDisplay:
      isComplete = self.display.parallel_log(message)
      # print('display bypass: ', message)
      pass
    if toPrint:
      print(message)
    sleep(delay)
    return isComplete

  def stats_log(self, stats, print = False):
    if self.display:
      self.display.stats_log(stats)
    if print:
      print(str(stats))

  def lcd_clear(self):
    if self.display:
      self.display.clear()

  def lcd_backlight(self, on = True):
    if self.display:
      self.display.backlight(on)

  def lcd_backlight_toggle(self):
    if self.display:
      self.display.backlight_toggle()

  def lcd_cycle_message(self):
    if self.display:
      self.display.cycle_message()

  def alert(self, message):
    isComplete = True
    if self.display:
      isComplete = self.display.parallel_log(message, True)
    print(message)
    return isComplete

