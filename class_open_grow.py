import yaml
import interface.lcd.class_lcd_manager as lcd_manager
import interface.class_interface as interface

class OpenGrow:
  def __init__(self):
    self.build_config()
    self.prep_components()

  def prep_components(self):
    if self.get_config('INTERFACE'):
      self.prep_interface()

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

  def prep_display(self):
    if self.get_config(['INTERFACE', 'LCD']):
      args = {
        'columns': self.get_config(['INTERFACE', 'LCD', 'LCDCOLS']),
        'rows': self.get_config(['INTERFACE', 'LCD', 'LCDROWS']),
        'text_cols': self.get_config(['INTERFACE', 'LCD', 'LCDTEXTCOLS']),
      }
      self.display = lcd_manager.LcdManager(args)

  def prep_interface(self):
    # self.prep_display()
    self.interface = interface.InterfaceManager(self.get_config(['INTERFACE']))

  def stats_screen(self):
    stats_list = self.get_config(['INTERFACE', 'LCD', 'STATSCREEN', 'STATS'], ['TIME'])
    stats_with_vals = []
    for stat in stats_list:
      stats_with_vals.append([stat, self.get_stat(stat)])
    self.interface.stats_screen(stats_with_vals)

  def get_stat(self, stat):
    match stat:
      case 'TIME':
        return '5:00 AM'
      case default:
        return 'N/A'