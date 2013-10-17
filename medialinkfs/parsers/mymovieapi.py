API_BASE = 'http://mymovieapi.com/'

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
MATCH_THRESHOLD = 0.8
def get_metadata(path, settings={}):
	name = os.path.basename(path)
	yearfound = yearfinder.search(name)
	year = None
	if yearfound:
		name = yearfinder.sub('',name).strip()
		year = yearfound.group(1)
	logger.debug("Loading metadata for %s"%name)
	result = search_title(name, year, settings)
	if not result:
		logger.debug("Found no metadata for %s"%name)
	return result

def squash(s):
	# normalize some weird characters first
	replacements = {'ː':':'}
	for f,t in replacements.items():
		s = s.replace(f,t)
	return re.sub(notislettermatcher, ' ', s.lower())

def api_type_str(type):
	types = {
	  'movie': 'm',
	  'tv movie': 'tv',
	  'tv series': 'tvs',
	  'video': 'v',
	  'video game': 'vg'
	}
	if type in types:
		return types[type]
	return 'none'

def find_best_match(name, results):
	best = 0
	bestresult = None
	for result in results:
		s = difflib.SequenceMatcher(None, squash(name), squash(result['title']))
		score = s.ratio()
		logger.debug("Search result %s scored %s"%(result['title'], score))
		if score > best and score > MATCH_THRESHOLD:
			best = score
			bestresult = result
	return bestresult

def search_title(name, year=None, settings={}):
	url = API_BASE+"?type=json&plot=none&episode=0&limit=5&aka=simple&lang=en-US&release=simple&title="+urllib.parse.quote(squash(name))
	if year:
		url += "&yg=1&year="+year
	if 'type' in settings:
		url += "&mt="+api_type_str(settings['type'])

	logger.debug("Searching from %s"%url)
	resource = urllib.request.urlopen(url)
	time.sleep(2)	# api rate limit
	raw_data = resource.read()
	text_data = raw_data.decode('utf-8')
	data = json.loads(text_data)
	if isinstance(data, list):	# results
		result = find_best_match(name, data)
		if result:
			return parse_response(result)
	return None
	
def parse_response(data):
	logger.debug("Found %s (%s)"%(data['title'],data['imdb_id']))
	result = {}
	result['genres'] = data['genres']
	result['actors'] = data['actors']
	result['year'] = int(data['year'])
	if 'rated' in data:
		result['rated'] = data['rated']
	return result
