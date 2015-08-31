API_BASE = 'http://myapifilms.com/imdb'

import os.path
import urllib
import urllib.request
import urllib.parse
import json
import logging
import re
import difflib
import time

logger = logging.getLogger(__name__)

splitter = re.compile('\s*,\s*')
yearfinder = re.compile('\(([12][0-9]{3})(-[12][0-9]{3})?\)')
notislettermatcher = re.compile('[^\w¢]', re.UNICODE)

_last_time = 0	# enforce a sleep of 2 seconds between calls

def get_metadata(metadata, settings={}):
	path = metadata['path']
	if 'name' in metadata:
		name = metadata['name']
		year = metadata.get('year')
	else:
		name = os.path.basename(path)
		yearfound = yearfinder.search(name)
		year = None
		if yearfound:
			name = yearfinder.sub('',name).strip()
			year = yearfound.group(1)
	logger.debug("Loading metadata for %s from MyApiFilms"%name)
	result = search_title(name, year, settings)
	if not result:
		logger.debug("Found no metadata for %s from MyApiFilms"%name)
	return result

def squash(s):
	# normalize some weird characters first
	replacements = {'ː':':'}
	for f,t in replacements.items():
		s = s.replace(f,t)
	return re.sub(notislettermatcher, ' ', s.lower())

def api_type_str(type):
	types = {
	  'movie': 'M',
	  'tv movie': 'TV',
	  'tv series': 'TV',
	  'video': 'N',
	  'video game': 'VG'
	}
	if type in types:
		return types[type]
	return 'none'


def search_title(name, year=None, settings={}):
	url = API_BASE+"?type=json&actors=S&lang=en-us&title="+urllib.parse.quote(squash(name))
	if year:
		url += "&forceYear=1&year="+str(year)
	if 'type' in settings:
		url += "&filter="+api_type_str(settings['type'])
	if 'api_key' in settings:
		url += "&token="+settings['api_key']

	logger.debug("Searching from %s"%url)

	# api rate limit
	global _last_time
	delay = _last_time + 2 - time.time()
	if delay > 0: time.sleep(delay)
	_last_time = time.time()

	resource = urllib.request.urlopen(url)
	raw_data = resource.read()
	text_data = raw_data.decode('utf-8')
	data = json.loads(text_data)
	if isinstance(data, list):	# results
		result = data[0];
		if result:
			return parse_response(result)
	return None
	
def parse_response(data):
	if 'title' in data: logger.debug("Found %s (%s)"%(data['title'],data['idIMDB']))
	result = {}
	if 'actors' in data: result['actors'] = [a['actorName'] for a in data['actors']]
	if 'genres' in data: result['genres'] = data['genres']
	if 'year' in data: result['year'] = int(data['year'][0:4])
	if 'rating' in data: 
		result['rating'] = float(data['rating'])
		logger.debug("Found rating of %s"%data['rating'])
	if 'metascore' in data: result['metascore'] = data['metascore']
	return result
