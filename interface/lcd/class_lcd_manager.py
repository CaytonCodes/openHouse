from smbus import SMBus
from time import sleep
from _common_funcs import settings_update, error_builder

ALIGN_FUNC = {
	'left': 'ljust',
	'right': 'rjust',
	'center': 'center'}
CLEAR_DISPLAY = 0x01
ENABLE_BIT = 0b00000100
LINES = {
	1: 0x80,
	2: 0xC0,
	3: 0x94,
	4: 0xD4}

LCD_BACKLIGHT = 0x08
LCD_NOBACKLIGHT = 0x00

class LcdManager(object):

	def __init__(self, args):
		self.settings = {
			'COLS': 20,
			'ROWS': 4,
			'TEXT_COLS': 1,
			'ADDRESS': 0x27,
			'I2C_BUS_NUM': 1,
			'BACKLIGHT': True
		}
		settings_update(self.settings, args)
		self.address = self.settings['ADDRESS']
		self.bus = SMBus(self.settings['I2C_BUS_NUM'])
		self.delay = 0.0005
		self.rows = self.settings['ROWS']
		self.width = self.settings['COLS']
		self.backlight_status = self.settings['BACKLIGHT']
		self.message = ''
		self.messageRemainder = ''
		self.holdScreen = False

		self.write(0x33)
		self.write(0x32)
		self.write(0x06)
		self.write(0x0C)
		self.write(0x28)
		self.write(CLEAR_DISPLAY)
		sleep(self.delay)

	def _write_byte(self, byte):
		self.bus.write_byte(self.address, byte)
		self.bus.write_byte(self.address, (byte | ENABLE_BIT))
		sleep(self.delay)
		self.bus.write_byte(self.address,(byte & ~ENABLE_BIT))
		sleep(self.delay)

	def write(self, byte, mode=0):
		backlight_mode = LCD_BACKLIGHT if self.backlight_status else LCD_NOBACKLIGHT
		self._write_byte(mode | (byte & 0xF0) | backlight_mode)
		self._write_byte(mode | ((byte << 4) & 0xF0) | backlight_mode)

	def _text(self, text, line, align='left', noStrip = False):
		if line > self.rows:
			return text
		excess = None
		self.write(LINES.get(line, LINES[1]))
		text, other_lines = self.get_text_line(text, noStrip)
		text = getattr(text, ALIGN_FUNC.get(align, 'ljust'))(self.width)
		for char in text:
			self.write(ord(char), mode=1)
		if other_lines:
			excess = self._text(other_lines, line + 1, align=align, noStrip = noStrip)
		return excess

	def _newText(self, text, line, align='left', noStrip = False):
		self.clear()
		return self._text(text, line, align, noStrip)

	def parallel_log(self, text = None, holdScreen = False, isStats = False):
		# Logs text to LCD screen. If text is None or same as previous call, cycles through screens of message (for longer messages). Hold screen prevents message from being overwritten until completely cycled through.
		# Returns true if message is completely cycled through.
		if not text or text == self.message:
			if self.messageRemainder and self.messageRemainder.strip():
				self.messageRemainder = self._newText(self.messageRemainder, 1, noStrip = isStats)
				return False
			else:
				# We've cycled through the message.
				self.message = ''
				self.messageRemainder = ''
				self.holdScreen = False
				return True
		else:
			self.message = text
			self.messageRemainder = self._newText(self.message, 1, noStrip = isStats)
			self.holdScreen = holdScreen
			return False

	def backlight(self, turn_on=True):
		self.backlight_status = turn_on
		self.write(0)

	def get_text_line(self, text, noStrip = False):
		line_break = self.width
		if len(text) > self.width:
			(line_break) = text[:self.width + 1].rfind(' ')
		if line_break < 0:
			line_break = self.width
		excess = text[line_break:] if noStrip else text[line_break:].strip()
		return text[:line_break], excess

	def stats_log(self, stats):
		# Stats is a dictionary of stats to be displayed of format {statName: Value}.
		if self.holdScreen:
			return
		width = self.width
		textColWidth = width // self.settings['TEXT_COLS']
		text = ''
		labels = ''
		vals = ''
		count = 0
		for statName, statVal in stats.items():
			count += 1
			statName = self._stat_prepper(statName, textColWidth)
			statVal = self._stat_prepper(statVal, textColWidth, True)
			labels += statName
			vals += statVal
			if count % self.settings['TEXT_COLS'] == 0:
				text += labels.center(width) + vals.center(width)
				labels = ''
				vals = ''
		text += labels.center(width) + vals.center(width)
		return self.parallel_log(text, 1, isStats = True)

	def cycle_message(self):
		self.parallel_log()

	def _stat_prepper(self, stat, textColWidth, isVal = False):
		offset = 0 if isVal else 1
		stat = stat.strip()
		if len(stat) > textColWidth - offset:
			stat = stat[:textColWidth - offset]
		if not isVal:
			stat += ':'
		stat = stat.center(textColWidth)
		return stat

	def clear(self):
		self.write(CLEAR_DISPLAY)
