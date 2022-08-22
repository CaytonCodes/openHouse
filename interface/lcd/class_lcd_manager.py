from smbus import SMBus
from comms.class_i2c_device import I2CDevice as I2CDevice
from time import sleep
from _common_funcs import _settings_update, _error_builder

# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMEN = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

# flags for backlight control
LCD_BACKLIGHT = 0x08
LCD_NOBACKLIGHT = 0x00

En = 0b00000100  # Enable bit
Rw = 0b00000010  # Read/Write bit
Rs = 0b00000001  # Register select bit


ALIGN_FUNC = {
	'left': 'ljust',
	'right': 'rjust',
	'center': 'center'}

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
			'BACKLIGHT': True,
			'PROTOCOL': 'I2C',
			'PROTOCOL_ARGS': {
				'I2C_ADDR': 0x27,
				'I2C_BUS_NUM': 1,
				'STD_DELAY': 0.0005,
				'ENCODING': 'bytes',
			}
		}
		_settings_update(self.settings, args)
		self.address = 0x27

		# self.bus = SMBus(self.settings['PROTOCOL_ARGS']['I2C_BUS_NUM'])

		self.delay = self.settings['PROTOCOL_ARGS']['STD_DELAY']
		self.rows = self.settings['ROWS']
		self.cols = self.settings['COLS']

		self._setup_comms()

		self.backlight_status = self.settings['BACKLIGHT']
		self.message = ''
		self.messageRemainder = ''
		self.holdScreen = False

		self.write(0x33)
		self.write(0x32)
		self.write(0x06)
		self.write(0x0C)
		self.write(0x28)
		self.write(LCD_CLEARDISPLAY)
		sleep(self.delay)

	def _setup_comms(self):
		if self.settings.get('PROTOCOL') == 'I2C':
			protocolArgs = self.settings.get('PROTOCOL_ARGS', {})
			protocolArgs['DEVICE_NAME'] = 'LCD'
			protocolArgs['ENCODING'] = 'bytes'
			self.comm = I2CDevice(protocolArgs)

	def _write_byte(self, byte):
		self.comm.write_byte(byte)
		self.comm.write_byte((byte | En))
		sleep(self.delay)
		self.comm.write_byte((byte & ~En))
		sleep(self.delay)

	def _write_byte_old(self, byte):
		print('old bytes: ', byte)
		self.bus.write_byte(self.address, byte)
		self.bus.write_byte(self.address, (byte | En))
		sleep(self.delay)
		self.bus.write_byte(self.address,(byte & ~En))
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
		text = getattr(text, ALIGN_FUNC.get(align, 'ljust'))(self.cols)
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

	def backlight_toggle(self):
		self.backlight_status = not self.backlight_status
		self.write(0)

	def get_text_line(self, text, noStrip = False):
		line_break = self.cols
		if len(text) > self.cols:
			(line_break) = text[:self.cols + 1].rfind(' ')
		if line_break < 0:
			line_break = self.cols
		excess = text[line_break:] if noStrip else text[line_break:].strip()
		return text[:line_break], excess

	def stats_log(self, stats):
		# Stats is a dictionary of stats to be displayed of format {statName: Value}.
		if self.holdScreen:
			return
		cols = self.cols
		textColWidth = cols // self.settings['TEXT_COLS']
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
				text += labels.center(cols) + vals.center(cols)
				labels = ''
				vals = ''
		text += labels.center(cols) + vals.center(cols)
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
		self.write(LCD_CLEARDISPLAY)
