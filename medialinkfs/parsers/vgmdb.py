API_BASE = 'http://vgmdb.info/'
MATCH_THRESHOLD = 0.7

import os.path
import urllib
import urllib.request
import urllib.parse
import json
import difflib
import re
import logging

logger = logging.getLogger(__name__)

class Module(object):
	islettermatcher = re.compile('[A-Za-z0-9]')
	notislettermatcher = re.compile('[^A-Za-z0-9]')

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
		else:
			name = os.path.basename(path)
		logger.debug("Loading metadata for %s"%name)
		(result, otherresults) = self.search_for_album(name)
		if not result:
			logger.debug("Found no metadata for %s"%name)
			return (result, otherresults)	# couldn't find a match
		album_data = self.load_json_data(result['link'])
		franchises = self.load_album_franchises(album_data)
		data = {}
		for type in ['arrangers', 'composers', 'lyricists', 'performers']:
			if type in album_data:
				data[type] = [x['names']['en'] for x in album_data[type]]
		if 'products' in album_data:
			data['games'] = [x['names']['en'] for x in album_data['products']]
		if 'release_date' in album_data:
			data['year'] = album_data['release_date'][0:4]
		if len(album_data['composers']) > 0:
			data['artists'] = [x['names']['en'] for x in album_data['composers']]
			data['artist'] = data['artists'][0]
		if len(franchises) > 0:
			data['franchise'] = franchises[0]['name']
			data['franchises'] = [x['name'] for x in franchises]
		return (data, otherresults)

	def search_for_album(self, name):
		name = Module.squash(name)
		url = API_BASE+"search/albums/"+urllib.parse.quote(name)+"?format=json"
		logger.debug("Searching for album at %s"%(url,))
		resource = urllib.request.urlopen(url)
		raw_data = resource.read()
		text_data = raw_data.decode('utf-8')
		data = json.loads(text_data)
		results = data['results']['albums']
		(result, otherresults) = self.find_match(name, results)
		return (result, otherresults)

	@staticmethod
	def squash(s):
		return re.sub(Module.notislettermatcher, ' ', s.lower())

	def find_match(self, name, results):
		best = 0
		bestresult = None
		otherresults = []
		for result in results:
			score = Module.score_best_match(name, result['titles'].values())
			logger.debug("Search result %s scored %s"%(result['titles']['en'], score))
			if score > best and score > MATCH_THRESHOLD:
				best = score
				bestresult = result
			# todo
			#if score == best and score > MATCH_THRESHOLD:
			#	# older albums win
			#	if result['release_date'] < bestresult['release_date']:
			#		best = score
			#		bestresult = result
		otherresults = list(results)
		if bestresult:
			otherresults.remove(bestresult)
		return (bestresult, otherresults)

	@staticmethod
	def score_best_match(name, matches):
		best = 0
		name = Module.squash(name)
		for match in matches:
			match = Module.squash(match)
			s = difflib.SequenceMatcher(None, name.strip(), match.strip())
			best = max(best, s.ratio())
		return best

	def load_json_data(self, link):
		if link[0] == '/':
			link = link[1:]
		url = API_BASE+link
		resource = urllib.request.urlopen(url)
		raw_data = resource.read()
		text_data = raw_data.decode('utf-8')
		data = json.loads(text_data)
		return data

	def load_album_franchises(self, album_data):
		franchises_data = []
		if 'products' in album_data:
			for product in album_data['products']:
				franchises_data.extend(self.load_product_franchises(product))
		return franchises_data

	def load_product_franchises(self, product):
		franchises_data = []
		if 'link' not in product:
			return franchises_data
		product_data = self.load_json_data(product['link'])
		if 'franchises' in product_data:
			for franchise in product_data['franchises']:
				franchises_data.append(self.load_json_data(franchise['link']))
		if 'products' in product_data:
			for product in product_data['products']:
				franchises_data.extend(self.load_product_franchises(product))
		return franchises_data
