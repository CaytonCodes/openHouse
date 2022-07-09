#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Import necessary libraries for communication and display use
import drivers
from time import sleep


class LcdManager:
		def __init__(self, columns=16, rows=4):
				if columns > 16:
						columns = 16
				if rows > 4:
						rows = 4
				self.columns = columns
				self.rows = rows
				# Load the driver and set it to "display"
				self.display = drivers.Lcd()

		def check_inputs(self, num_line, num_cols=None):
				num_line_out = num_line if num_line <= self.rows else self.rows
				num_cols_out = num_cols if num_cols <= self.columns else self.columns
				return num_line_out, num_cols_out

		def long_string(self, text='', num_line=1, num_cols=None):
				"""
				Parameters: (driver, string to print, number of line to print, number of columns of your display)
				Return: This function send to display your scrolling string.
				"""
				num_line, num_cols = self.check_inputs(num_line, num_cols)
				if len(text) > num_cols:
						self.display.lcd_display_string(text[:num_cols], num_line)
						sleep(1)
						for i in range(len(text) - num_cols + 1):
								text_to_print = text[i:i+num_cols]
								self.display.lcd_display_string(text_to_print, num_line)
								sleep(0.2)
						sleep(1)
				else:
						self.display.lcd_display_string(text, num_line)

		def clear(self):
				self.display.lcd_clear()

		def write(self, text, num_line=1):
				self.long_string(text, num_line, self.columns)

		def write_line(self, text, num_line=1):
				self.long_string(text, num_line, self.columns)

		def write_line_clear(self, text, num_line=1):
				self.long_string(text, num_line, self.columns)
				self.display.lcd_clear()

		def write_line_clear_wait(self, text, num_line=1):
				self.long_string(text, num_line, self.columns)
				self.display.lcd_clear()
				sleep(1)

		def write_line_wait(self, text, num_line=1):
				self.long_string(text, num_line, self.columns)
				sleep(1)

		def write_line_wait_clear(self, text, num_line=1):
				self.long_string(text, num_line, self.columns)
				sleep(1)
				self.display.lcd_clear()
