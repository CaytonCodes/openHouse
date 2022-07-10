import yaml
import interface.lcd.class_lcd_manager as lcd_manager

class OpenHouse:
  def __init__(self):
    self.build_config()
    self.prep_display()

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