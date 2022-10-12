#!/usr/bin/env python

from devices.class_device import Device

class DisplayDevice(Device):
	def __init__(self, args, commManager = None):
		if 'PROTOCOL_ARGS' not in args.keys():
			args['PROTOCOL_ARGS'] = {}
		for arg in args:
			if arg != 'PROTOCOL_ARGS':
				args['PROTOCOL_ARGS'][arg] = args[arg]
		super().__init__(args, 'Display', 'interface', commManager)
		self.clear()

	def parallel_log(self, text = None, holdScreen = False, isStats = False):
		return self.comm.parallel_log(text, holdScreen, isStats)

	def stats_log(self, stats):
		return self.comm.stats_log(stats)

	def cycle_message(self):
		self.comm.parallel_log()

	def clear(self):
		self.comm.clear()

	def backlight(self, on):
		self.comm.backlight(on)

	def backlight_toggle(self):
		self.comm.backlight_toggle()

	def wake(self):
		self.comm.wake()

	def sleep(self):
		self.comm.sleep()

	def parallel_alert(self, period = 1, clear = False, text = None):
		self.comm.parallel_alert(period, clear, text)
