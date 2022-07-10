import lcd.class_lcd_manager as lcd_manager

class InterfaceManager:
  def __init__(self):
    self.display = lcd_manager.LcdManager()


  def list_scroll(self, text_list):
