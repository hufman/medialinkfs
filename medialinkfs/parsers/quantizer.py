""" Module to do a few cleanup things
Creates a decade metadata based on year
"""

import logging


logger = logging.getLogger(__name__)


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
	

	ratings = quantize_rating_ratings(cur_metadata)
	if ratings:
		new_metadata['ratings'] = "%s"%(ratings,)

	letter = quantize_name_letter(cur_metadata)
	if letter:
		new_metadata['letter'] = "%s"%(letter,)

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
		decade = int(int(year)/10) * 10
	return decade


def quantize_rating_ratings(metadata):
	key = None
	ratings = None
	for possible_key in ['rating']:
		if possible_key in metadata:
			key = possible_key
	if key:
		rating = int(float(metadata[key])*10)
		ratings = int(5 * round(float(rating)/5))/10  #sort into bins of 0.5
	return ratings

def quantize_name_letter(metadata):
	try:
		logger.debug("Trying to quantize name to letter")
		if 'name' in metadata:
			logger.debug("Quantizing %s into letter"%metadata['name'])
			letter = metadata['name'][0]
			if letter.isalpha():
				logger.debug("Matched letter %s"%letter)
				return letter
			else:
				return '0' #numbers/special characters go into the '0' bin
	except:
		raise
		pass

