#! /usr/bin/env python
# -*- coding: utf-8 -*-

# from .drivers import i2c_dev
from time import sleep
from comms.class_i2c_device import I2CDevice
from _common_funcs import settings_update, error_builder

# other commands
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
LCD_ENTRYSHIFTDECREMENT = 0x00

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


class LcdManager:
	def __init__(self, args):
		self.settings = {
			'COLS': 20,
			'ROWS': 4,
			'TEXT_COLS': 1,
			'ADDRESS': 0x27,
			'I2C_BUS_NUM': None,
		}
		settings_update(self.settings, args)
		i2cArgs = {
			'SENSOR_NAME': 'lcd',
			'I2C_ADDRESS': self.settings['ADDRESS'],
			'I2C_BUS_NUM': self.settings['I2C_BUS_NUM'],
		}
		self.display = I2CDevice(i2cArgs)
		# self.display = i2c_dev.Lcd()

	def write_cmd(self, cmd, mode=0):
		self.display.write(cmd, False, False)


	def check_inputs(self, num_line, num_cols=None):
		if num_cols is None:
			num_cols = self.settings['COLS']
		num_line_out = num_line if num_line <= self.settings['ROWS'] else self.settings['ROWS']
		num_cols_out = num_cols if num_cols <= self.settings['COLS'] else self.settings['COLS']
		return num_line_out, num_cols_out

	def long_string(self, text='', num_line=1, num_cols=None, col_offset=0):
		"""
		Parameters: (driver, string to print, number of line to print, number of columns of your display)
		Return: This function send to display your scrolling string.
		"""
		num_line, num_cols = self.check_inputs(num_line, num_cols)
		offset_string = " " * col_offset
		if col_offset + len(text) > num_cols:
			self.display.lcd_display_string(offset_string + text[:num_cols], num_line)
			sleep(1)
			for i in range(len(text) - num_cols + 1):
				text_to_print = text[i:i+num_cols]
				self.display.lcd_display_string(offset_string + text_to_print, num_line)
				sleep(0.2)
			sleep(1)
		else:
			self.display.lcd_display_string(offset_string + text, num_line)

	def stats_list(self, stats_list, multi_col = False):
		# Stats list is a list of tuples with the following format: (stat_name, stat_value)
		if multi_col:
			text_col_count = self.settings['TEXT_COLS']
			text_col_width = self.settings['COLS'] // text_col_count
		else:
			text_col_count = 1
			text_col_width = self.settings['COLS']
		centering_offset = (self.settings['COLS'] - text_col_count * text_col_width) // 2
		centering_offset = 0 if centering_offset < 0 else centering_offset
		rows = ['', '']
		for i in range(len(stats_list)):
			row = (i // text_col_count) * 2
			text_col = i % text_col_count
			col_offset = centering_offset + text_col * text_col_width
			# print(stats_list[i], row, text_col, col_offset)
			for x in [0, 1]:
				offset_string = " " * (text_col_width - len(stats_list[i][x]))
				rows[x] = rows[x] + stats_list[i][x] + offset_string
				# print(rows[x], col_offset - len(stats_list[i][x]))
				if text_col == text_col_count - 1:
					self.long_string(rows[x], row + x + 1)
					rows[x] = ''
			sleep(1)



	def clear(self):
			self.display.lcd_clear()

	def write(self, text, num_line=1):
			self.long_string(text, num_line, self.settings['COLS'])

	def write_line(self, text, num_line=1):
			self.long_string(text, num_line, self.settings['COLS'])

	def write_line_clear(self, text, num_line=1):
			self.long_string(text, num_line, self.settings['COLS'])
			self.display.lcd_clear()

	def write_line_clear_wait(self, text, num_line=1):
			self.long_string(text, num_line, self.settings['COLS'])
			self.display.lcd_clear()
			sleep(1)

	def write_line_wait(self, text, num_line=1):
			self.long_string(text, num_line, self.settings['COLS'])
			sleep(1)

	def write_line_wait_clear(self, text, num_line=1):
			self.long_string(text, num_line, self.settings['COLS'])
			sleep(1)
			self.display.lcd_clear()
