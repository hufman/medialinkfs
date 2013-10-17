""" Test module to assist with unit tests
Fill in the data variable keyed on the basename
"""
data = {}

import os.path

def get_metadata(path, settings={}):
	name = os.path.basename(path)
	if name in data:
		return data[name]
	else:
		return None
