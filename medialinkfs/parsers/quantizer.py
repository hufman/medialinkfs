""" Module to do a few cleanup things
Creates a decade metadata based on year
"""

def get_metadata(metadata, settings={}):
	cur_metadata = dict(metadata)
	new_metadata = {}
	year = quantize_releasedate_year(cur_metadata)
	if year:
		new_metadata['year'] = year

	cur_metadata.update(new_metadata)

	decade = quantize_year_decades(cur_metadata)
	if decade:
		new_metadata['decade'] = "%s"%(decade,)
		new_metadata['decades'] = "%ss"%(decade,)
	return new_metadata

def quantize_releasedate_year(metadata):
	try:
		if 'release_date' in metadata and \
		   len(metadata['release_date'])>=4:
			year = int(metadata['release_date'][0:4])
			return year
	except:
		raise
		pass

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
