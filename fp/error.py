__author__ = 'rychol'


class Error(Exception):
	def __init__(self, arg):
		self.args = arg
		self.message = arg