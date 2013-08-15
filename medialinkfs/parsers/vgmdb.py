API_BASE = 'http://hufman.dyndns.org/vgmdb/'
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

islettermatcher = re.compile('[A-Za-z0-9]')
notislettermatcher = re.compile('[^A-Za-z0-9]')
def get_metadata(path):
	name = os.path.basename(path)
	logger.debug("Loading metadata for %s"%name)
	result = search_for_album(name)
	if not result:
		logger.debug("Found no metadata for %s"%name)
		return None	# couldn't find a match
	album_data = load_json_data(result['link'])
	franchises = load_album_franchises(album_data)
	data = {}
	for type in ['composers', 'lyricists', 'performers']:
		if type in album_data:
			data[type] = [x['names']['en'] for x in album_data[type]]
	if len(album_data['composers']) > 0:
		data['artists'] = [x['names']['en'] for x in album_data['composers']]
		data['artist'] = data['artists'][0]
	if len(franchises) > 0:
		data['franchise'] = franchises[0]['name']
		data['franchises'] = [x['name'] for x in franchises]
	return data

def search_for_album(name):
	url = API_BASE+"search/albums/"+urllib.parse.quote(name)+"?format=json"
	logger.debug("Searching for album at %s"%(url,))
	resource = urllib.request.urlopen(url)
	raw_data = resource.read()
	text_data = raw_data.decode('utf-8')
	data = json.loads(text_data)
	results = data['results']['albums']
	result = find_match(name, results)
	return result

def find_match(name, results):
	best = 0
	bestresult = None
	for result in results:
		score = score_best_match(name, result['titles'].values())
		logger.debug("Search result %s scored %s"%(result['titles']['en'], score))
		if score > best and score > MATCH_THRESHOLD:
			best = score
			bestresult = result
	return bestresult

def score_best_match(name, matches):
	best = 0
	name = name.lower()
	name = re.sub(notislettermatcher, ' ', name)
	for match in matches:
		match = match.lower()
		match = re.sub(notislettermatcher, ' ', match)
		s = difflib.SequenceMatcher(None, name.strip(), match.strip())
		best = max(best, s.ratio())
	return best

def load_json_data(link):
	if link[0] == '/':
		link = link[1:]
	url = API_BASE+link
	resource = urllib.request.urlopen(url)
	raw_data = resource.read()
	text_data = raw_data.decode('utf-8')
	data = json.loads(text_data)
	return data

def load_album_franchises(album_data):
	franchises_data = []
	if 'products' in album_data:
		for product in album_data['products']:
			franchises_data.extend(load_product_franchises(product))
	return franchises_data

def load_product_franchises(product):
	franchises_data = []
	if 'link' not in product:
		return franchises_data
	product_data = load_json_data(product['link'])
	if 'franchises' in product_data:
		for franchise in product_data['franchises']:
			franchises_data.append(load_json_data(franchise['link']))
	if 'products' in product_data:
		for product in product_data['products']:
			franchises_data.extend(load_product_franchises(product))
	return franchises_data
