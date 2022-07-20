#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Import necessary libraries for communication and display use
from .drivers import i2c_dev
from time import sleep


class LcdManager:
		def __init__(self, args):
				self.settings = {
					'columns': 20,
					'rows': 4,
					'text_cols': 1,
				}
				# Load the driver and set it to "display"
				self.display = i2c_dev.Lcd()
				self.settings.update(args)

		def check_inputs(self, num_line, num_cols=None):
				if num_cols is None:
						num_cols = self.settings['columns']
				num_line_out = num_line if num_line <= self.settings['rows'] else self.settings['rows']
				num_cols_out = num_cols if num_cols <= self.settings['columns'] else self.settings['columns']
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
					text_col_count = self.settings['text_cols']
					text_col_width = self.settings['columns'] // text_col_count
				else:
					text_col_count = 1
					text_col_width = self.settings['columns']
				centering_offset = (self.settings['columns'] - text_col_count * text_col_width) // 2
				centering_offset = 0 if centering_offset < 0 else centering_offset
				rows = ['', '']
				for i in range(len(stats_list)):
						row = (i // text_col_count) * 2
						text_col = i % text_col_count
						col_offset = centering_offset + text_col * text_col_width
						print(stats_list[i], row, text_col, col_offset)
						for x in [0, 1]:
								offset_string = " " * (text_col_width - len(stats_list[i][x]))
								rows[x] = rows[x] + stats_list[i][x] + offset_string
								print(rows[x], col_offset - len(stats_list[i][x]))
								if text_col == text_col_count - 1:
									self.long_string(rows[x], row + x + 1)
									rows[x] = ''
						sleep(1)



		def clear(self):
				self.display.lcd_clear()

		def write(self, text, num_line=1):
				self.long_string(text, num_line, self.settings['columns'])

		def write_line(self, text, num_line=1):
				self.long_string(text, num_line, self.settings['columns'])

		def write_line_clear(self, text, num_line=1):
				self.long_string(text, num_line, self.settings['columns'])
				self.display.lcd_clear()

		def write_line_clear_wait(self, text, num_line=1):
				self.long_string(text, num_line, self.settings['columns'])
				self.display.lcd_clear()
				sleep(1)

		def write_line_wait(self, text, num_line=1):
				self.long_string(text, num_line, self.settings['columns'])
				sleep(1)

		def write_line_wait_clear(self, text, num_line=1):
				self.long_string(text, num_line, self.settings['columns'])
				sleep(1)
				self.display.lcd_clear()
