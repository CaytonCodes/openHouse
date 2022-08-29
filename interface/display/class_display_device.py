from devices.class_device import Device

class DisplayDevice(Device):
	def __init__(self, args, commManager = None):
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
