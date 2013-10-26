""" Module to do a few cleanup things
Creates a decade metadata based on year
"""

def get_metadata(metadata, settings={}):
	new_metadata = {}
	decade = quantize_year_decades(metadata)
	if decade:
		new_metadata['decade'] = "%s"%(decade,)
		new_metadata['decades'] = "%ss"%(decade,)
	return new_metadata

def quantize_year_decades(metadata):
	key = None
	decade = None
	for possible_key in ['year','Year']:
		if possible_key in metadata:
			key = possible_key
	if key:
		year = int(metadata[key])
		decade = int(year/10) * 10
	return decade
