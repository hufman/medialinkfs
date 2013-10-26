""" Test module to assist with unit tests
Fill in the data variable keyed on the basename
"""
data = {}

import os.path

def get_metadata(metadata, settings={}):
	path = metadata['path']
	name = os.path.basename(path)
	if name in data:
		ret = dict(data[name])
		ret.update(settings)
		return ret
	else:
		return None
