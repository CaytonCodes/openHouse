import interface.lcd.class_lcd_manager as lcd_manager

class InterfaceManager:
  def __init__(self, config):
    self.config = config
    self.prep_components()

  def prep_components(self):
    if self.config['LCD']:
      self.prep_display()

  def prep_display(self):
    if self.config['LCD']:
      args = {
        'columns': self.config['LCD']['COLS'],
        'rows': self.config['LCD']['ROWS'],
        'text_cols': self.config['LCD']['TEXT_COLS'],
      }
      self.display = lcd_manager.LcdManager(args)

  def stats_screen(self, stats_list, clear = True):
    if self.display:
      if clear:
        self.display.clear()
      self.display.stats_list(stats_list, True)
