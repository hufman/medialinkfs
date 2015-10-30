""" Test module to assist with unit tests
Fill in the parser_options['data'] keyed on the item's basename
"""

import os.path

data = {}

class Module(object):
	def __init__(self, parser_options):
		self.data = parser_options.get('data', {})

	def get_metadata(self, metadata):
		path = metadata['path']
		name = os.path.basename(path)
		if name in self.data:
			ret = dict(self.data[name])
			return ret
		elif name in data:
			ret = dict(data[name])
			return ret
		else:
			return None
