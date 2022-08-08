from time import sleep
import interface.lcd.class_lcd_manager as lcd_manager
from interface.inputs.class_keyboard_watcher import KeyboardWatcher

class InterfaceManager:
  def __init__(self, config):
    self.config = config
    self.prep_components()

  def prep_components(self):
    if self.config['LCD']:
      self.prep_display()
    self.keyboard = KeyboardWatcher()

  def prep_display(self):
    if self.config['LCD']:
      args = {
        'columns': self.config['LCD']['COLS'],
        'rows': self.config['LCD']['ROWS'],
        'text_cols': self.config['LCD']['TEXT_COLS'],
      }
      self.display = lcd_manager.LcdManager(args)

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

  def log(self, message, delay = 0, forcePrint = False):
    toPrint = True if forcePrint or not self.display else False
    if self.display:
      # self.display.log(message)
      # print('display bypass: ', message)
      pass
    if toPrint:
      print(message)
    sleep(delay)


  def stats_screen(self, stats_list, clear = True):
    if self.display:
      if clear:
        self.display.clear()
      self.display.stats_list(stats_list, True)
