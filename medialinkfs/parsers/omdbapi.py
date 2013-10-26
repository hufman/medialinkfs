API_BASE = 'http://omdbapi.com/'

import os.path
import urllib
import urllib.request
import urllib.parse
import json
import logging
import re
import difflib

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
	result = load_title(name, year)
	if not result:
		result = search_title(name, year)
		if not result:
			logger.debug("Found no metadata for %s"%name)
	return result

def load_by_id(tt):
	url = API_BASE+"?f=json&i="+urllib.parse.quote(tt)
	resource = urllib.request.urlopen(url)
	raw_data = resource.read()
	text_data = raw_data.decode('utf-8')
	data = json.loads(text_data)
	return data

def load_title(name, year=None):
	url = API_BASE+"?f=json&t="+urllib.parse.quote(name)
	if year:
		url += "&y="+year
	logger.debug("Loading metadata from %s"%url)
	resource = urllib.request.urlopen(url)
	raw_data = resource.read()
	text_data = raw_data.decode('utf-8')
	data = json.loads(text_data)
	if 'Response' in data and data['Response']=='True':
		return parse_response(data)
	else:
		result = None
	return result

def squash(s):
	# normalize some weird characters first
	replacements = {'ː':':'}
	for f,t in replacements.items():
		s = s.replace(f,t)
	return re.sub(notislettermatcher, ' ', s.lower())

def find_best_match(name, results):
	best = 0
	bestresult = None
	for result in results:
		s = difflib.SequenceMatcher(None, squash(name), squash(result['Title']))
		score = s.ratio()
		logger.debug("Search result %s (%s) scored %s"%(result['Title'], result['imdbID'], score))
		if score > best and score > MATCH_THRESHOLD:
			best = score
			bestresult = result
	return bestresult

def search_title(name, year=None):
	url = API_BASE+"?f=json&s="+urllib.parse.quote(squash(name))
	if year:
		url += "&y="+year
	logger.debug("Searching from %s"%url)
	resource = urllib.request.urlopen(url)
	raw_data = resource.read()
	text_data = raw_data.decode('utf-8')
	data = json.loads(text_data)
	if not "Response" in data or data['Response']!="False":
		result = find_best_match(name, data['Search'])
		if result:
			id = result['imdbID']
			return parse_response(load_by_id(id))
	return None
	
def parse_response(data):
	logger.debug("Found %s (%s)"%(data['Title'],data['imdbID']))
	result = {}
	result['genres'] = splitter.split(data['Genre'])
	result['writers'] = splitter.split(data['Writer'])
	result['directors'] = splitter.split(data['Director'])
	result['actors'] = splitter.split(data['Actors'])
	result['rated'] = data['Rated']
	result['year'] = int(data['Year'])
	return result
