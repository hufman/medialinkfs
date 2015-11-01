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

class Module(object):
	splitter = re.compile('\s*,\s*')
	yearfinder = re.compile('\(([12][0-9]{3})(-[12][0-9]{3})?\)')
	notislettermatcher = re.compile('[^\w¢]', re.UNICODE)
	MATCH_THRESHOLD = 0.8

	def __init__(self, parser_options):
		self.parser_options = parser_options

	def get_metadata(self, metadata):
		""" Search for an item's metadata
		    Returns the best match, or None
		"""
		(result, otherresults) = self.search_metadata(metadata)
		return result

	def search_metadata(self, metadata):
		""" Search for an item's metadata
		    Returns a tuple of:
		      closest match, if any
		      all other close matches, sorted by descending closeness
		"""
		path = metadata['path']
		if 'name' in metadata:
			name = metadata['name']
			year = metadata.get('year')
		else:
			name = os.path.basename(path)
			yearfound = Module.yearfinder.search(name)
			year = None
			if yearfound:
				name = Module.yearfinder.sub('',name).strip()
				year = yearfound.group(1)
		logger.debug("Loading metadata for %s"%name)
		(result, otherresults) = self.load_title(name, year)
		if not result:
			(result, otherresults) = self.search_title(name, year)
			if not result:
				logger.debug("Found no metadata for %s"%name)
		return (result, otherresults)

	def load_by_id(self, tt):
		url = API_BASE+"?f=json&i="+urllib.parse.quote(tt)
		resource = urllib.request.urlopen(url)
		raw_data = resource.read()
		text_data = raw_data.decode('utf-8')
		data = json.loads(text_data)
		return data

	def load_title(self, name, year=None):
		url = API_BASE+"?f=json&t="+urllib.parse.quote(name)
		if year:
			url += "&y="+year
		logger.debug("Loading metadata from %s"%url)
		resource = urllib.request.urlopen(url)
		raw_data = resource.read()
		text_data = raw_data.decode('utf-8')
		data = json.loads(text_data)
		if 'Response' in data and data['Response']=='True':
			result = (self.parse_response(data), [])
		else:
			result = (None, [])
		return result

	@staticmethod
	def squash(s):
		# normalize some weird characters first
		replacements = {'ː':':'}
		for f,t in replacements.items():
			s = s.replace(f,t)
		return re.sub(Module.notislettermatcher, ' ', s.lower())

	def find_best_match(self, name, results):
		best = 0
		bestresult = None
		otherresults = []
		for result in results:
			s = difflib.SequenceMatcher(None, Module.squash(name), Module.squash(result['Title']))
			score = s.ratio()
			logger.debug("Search result %s (%s) scored %s"%(result['Title'], result['imdbID'], score))
			if score > best and score > Module.MATCH_THRESHOLD:
				best = score
				bestresult = result
		otherresults = list(results)
		if bestresult:
			otherresults.remove(bestresult)
		return (bestresult, otherresults)

	def search_title(self, name, year=None):
		url = API_BASE+"?f=json&s="+urllib.parse.quote(Module.squash(name))
		if year:
			url += "&y="+year
		logger.debug("Searching from %s"%url)
		resource = urllib.request.urlopen(url)
		raw_data = resource.read()
		text_data = raw_data.decode('utf-8')
		data = json.loads(text_data)
		if not "Response" in data or data['Response']!="False":
			(result, otherresults) = self.find_best_match(name, data['Search'])
			if result:
				id = result['imdbID']
				result = self.parse_response(self.load_by_id(id))
			return (result, otherresults)
		return (None, [])

	def parse_response(self, data):
		logger.debug("Found %s (%s)"%(data['Title'],data['imdbID']))
		result = {}
		if 'Genre' in data: result['genres'] = Module.splitter.split(data['Genre'])
		if 'Writer' in data: result['writers'] = Module.splitter.split(data['Writer'])
		if 'Director' in data: result['directors'] = Module.splitter.split(data['Director'])
		if 'Actors' in data: result['actors'] = Module.splitter.split(data['Actors'])
		if 'Rated' in data: result['rated'] = data['Rated']
		if 'Year' in data: result['year'] = int(re.sub('[^0-9]','',data['Year'])[0:4])
		return result
