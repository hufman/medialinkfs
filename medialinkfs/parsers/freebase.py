API_BASE = 'https://www.googleapis.com/freebase/v1/mqlread'

import os.path
import urllib
import urllib.request
import urllib.parse
import json
import logging
import re
import difflib
import time
import html.parser
HTMLParser = html.parser.HTMLParser()

logger = logging.getLogger(__name__)

splitter = re.compile('\s*,\s*')
yearfinder = re.compile('\(([12][0-9]{3})(-[12][0-9]{3})?\)')
notislettermatcher = re.compile('[^\w¢]', re.UNICODE)
MATCH_THRESHOLD = 0.8

# Rename an mql key to a shorter metadata key
key_renames = {
	'/common/topic/alias': 'aka',
	'/film/film/initial_release_date': 'release_date',
	'/film/film/directed_by': 'directors',
	'/film/film/starring': 'actors',
	'/film/film/genre': 'genres',
	'/film/film/subjects': 'subjects',
	'/film/film/film_series': 'series',
	'/film/film/produced_by': 'producers',
	'/film/film/written_by': 'writers',
	'/film/film/edited_by': 'editors',
	'/film/film/music': 'composers',
	'/film/film/language': 'languages',
	'/film/film/country': 'countries',
	'/tv/tv_program/regular_cast': 'actors',
	'/tv/tv_program/air_date_of_first_episode': 'release_date',
	'/tv/tv_program/genre': 'genres',
	'/tv/tv_program/tv_producer': 'producers',
	'/tv/tv_program/recurring_writers': 'writers',
	'/tv/tv_program/original_network': 'network',
	'/tv/tv_program/country_of_origin': 'countries',
	'/tv/tv_program/languages': 'languages'
}
# What object keys should be promoted to full things
key_promotions = {
	'/film/film/starring':'actor',
	'/tv/tv_program/regular_cast':'actor',
	'/tv/tv_program/original_network':'network',
	'/tv/tv_program/recurring_writers':'writer',
	'/tv/tv_program/tv_producer':'producer'
}
# properties use to search
# If the value is a string, use that element of the info object
# If the value is a lambda, try to run it against the info object
default_searches = {
	'_default':[{
		'name~=':'name'
		},{
		'/common/topic/alias~=':'name'
	}],
	'/film/film':[{
		'name~=':'name',
		'initial_release_date>=':lambda x:"%s-01-01"%(x['year']),
		'initial_release_date<=':lambda x:"%s-12-31"%(x['year'])
		},{
		'/common/topic/alias~=':'name',
		'initial_release_date>=':lambda x:"%s-01-01"%(x['year']),
		'initial_release_date<=':lambda x:"%s-12-31"%(x['year'])
	}],
	'/tv/tv_program':[{
		'type':'/tv/tv_program',
		'name~=':'name',
		'air_date_of_first_episode>=':lambda x:"%s-01-01"%(x['year']),
		'air_date_of_first_episode<=':lambda x:"%s-12-31"%(x['year'])
		},{
		'type':'/tv/tv_program',
		'/common/topic/alias~=':'name',
		'air_date_of_first_episode>=':lambda x:"%s-01-01"%(x['year']),
		'air_date_of_first_episode<=':lambda x:"%s-12-31"%(x['year'])
	}]
}
# what metadata properties every search will have
required_properties = {
	'mid': None,
	'name':None,
	'/common/topic/alias':[]
}
# What metadata properties to search for
default_properties = {
	'/film/film':{
		'/film/film/initial_release_date':None,
		'/film/film/directed_by':[],
		'/film/film/starring':[{'actor':None, 'optional':True}],
		'/film/film/genre':[],
		'/film/film/subjects':[],
		'/film/film/film_series':[],
		'/film/film/produced_by':[],
		'/film/film/written_by':[],
		'/film/film/edited_by':[],
		'/film/film/music':[],
		'/film/film/language':[],
		'/film/film/country':[]
	},
	'/tv/tv_program':{
		'/tv/tv_program/regular_cast':[{"actor":None, 'optional':True}],
		'/tv/tv_program/air_date_of_first_episode':None,
		'/tv/tv_program/genre':[],
		'/tv/tv_program/languages':[],
		'/tv/tv_program/tv_producer':[{"producer":None, 'optional':True}],
		'/tv/tv_program/recurring_writers':[{"writer":None, 'optional':True}],
		'/tv/tv_program/original_network':[{"network":None, 'optional':True}],
		'/tv/tv_program/country_of_origin':[]
	}
}

def get_metadata(metadata, settings={}):
	path = metadata['path']
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

def find_best_match(needle, results):
	best = 0
	bestresult = None
	for result in results:
		names = []
		if 'name' in result:
			names.append(result['name'])
		if '/common/topic/alias' in result:
			names.extend(result['/common/topic/alias'])
		for name in names:
			s = difflib.SequenceMatcher(None, squash(needle), squash(name))
			score = s.ratio()
			#logger.debug("Search result %s (%s) scored %s"%(name, result['mid'], score))
			if score > best and score > MATCH_THRESHOLD:
				best = score
				bestresult = result
	return bestresult

def expand_search(search, info):
	ret = {}
	for key,value in search.items():
		if isinstance(value, str):
			if value in info:
				ret[key] = info[value]
		elif hasattr(value, '__call__'):
			try:
				ret[key] = value(info)
			except:
				pass
	return ret

def rename_keys(result, renames=key_renames):
	ret = {}
	for key in result:
		if key in renames:
			ret[renames[key]] = result[key]
		else:
			ret[key] = result[key]
	return ret

def promote_keys(result, promotions=key_promotions):
	ret = {}
	for key in result:
		if key in promotions:
			pkey = promotions[key]
			if isinstance(result[key], list):
				ret[key] = [r[pkey] for r in result[key]]
			elif isinstance(result[key], dict):
				ret[key] = result[key][pkey]
		else:
			ret[key] = result[key]
	return ret

def cleanup_genres(info):
	if 'type' in info and \
	   info['type'] == '/film/film' and \
	   'genres' in info:
		for index in range(0,len(info['genres'])):
			genre = info['genres'][index]
			if genre[-5:] == ' Film':
				info['genres'][index] = genre[:-5]
	return info

def cleanup_freebase(info):
	if 'type' in info:
		info['freebase_type'] = info['type']
		del info['type']
	if 'name' in info:
		info['freebase_name'] = info['name']
		del info['name']
	return info

def cleanup_nulls(info):
	for key,value in info.items():
		if value == None:
			del info[key]
		if isinstance(value, dict):
			cleanup_nulls(info)
		if isinstance(value, list):
			cleanup_nulls_list(value)
	return info
def cleanup_nulls_list(info):
	index = 0
	while index < len(info):
		value = info[index]
		if value == None:
			info.pop(index)
			index -= 1
		if isinstance(value, dict):
			cleanup_nulls(value)
		if isinstance(value, list):
			cleanup_nulls_list(value)
		index += 1
	return info

def unescape_html_dict(info):
	for key,value in info.items():
		if isinstance(value, dict):
			unescape_html_dict(value)
		if isinstance(value, list):
			unescape_html_list(value)
		if isinstance(value, str):
			info[key] = HTMLParser.unescape(value)
	return info
def unescape_html_list(info):
	index = 0
	while index < len(info):
		value = info[index]
		if isinstance(value, dict):
			unescape_html_dict(value)
		if isinstance(value, list):
			unescape_html_list(value)
		if isinstance(value, str):
			info[index] = HTMLParser.unescape(value)
		index += 1
	return info

def search_title(name, year=None, settings={}):
	queries = []
	searches = []
	properties = {}
	renames = {}
	promotions = {}
	# load up default search options
	properties.update(required_properties)
	searches = default_searches['_default']
	if 'type' in settings:
		type = settings['type']
		if type in default_searches:
			searches = default_searches[type]
		if type in default_properties:
			properties.update(default_properties[type])
		properties['type'] = type
	else:
		properties['type'] = []
	renames = key_renames
	promotions = key_promotions
	# load up user-provided search options
	if 'searches' in settings:
		searches = settings['searches']
	for setting in ['properties','renames','promotions']:
		if setting in settings:
			locals()[setting].update(settings[setting])
	# generate object containing filename metadata
	search_info = {'name':name}
	if year:
		search_info['year'] = year
	# use that object to generate the search queries
	for search_tmpl in searches:
		search = expand_search(search_tmpl, search_info)
		search.update(properties)
		queries.append([search])	# mql needs it to be an array
	# run the search queries
	results = run_mql_queries(queries, settings)
	result = find_best_match(name, results)
	# handle partial search result
	if result and \
	   'mid' in result and \
	   'type' in result and \
	   'type' not in settings and \
	   'properties' not in settings:
		for type in result['type']:
			if type in default_properties:
				properties.update(default_properties[type])
		properties['mid'] = result['mid']
		# generate the search query
		query = [properties] # mql needs it to be an array
		# run the search query
		results = run_mql_query(query, settings)
		result = find_best_match(name, results)
	# clean up the result
	if result:
		result = promote_keys(result, promotions)
		result = rename_keys(result, renames)
		result = cleanup_genres(result)
		result = cleanup_freebase(result)
		result = cleanup_nulls(result)
	return result

def run_mql_queries(queries, settings={}):
	results = []
	for query in queries:
		data = run_mql_query(query, settings)
		results.extend(data)
	return results
	
def run_mql_query(query, settings):
	results = []
	try:
		headers = {'Content-Type': 'application/json'}
		params = {'query': json.dumps(query)}
		if "api_key" in settings:
			params['key'] = settings['api_key']
		url = API_BASE + '?' + urllib.parse.urlencode(params)
		logger.debug("Searching from %s"%url)
		resource = urllib.request.urlopen(url)
		raw_data = resource.read()
		text_data = raw_data.decode('utf-8')
		data = json.loads(text_data)
		if 'result' in data:
			results = data['result']
		unescape_html_list(results)
	except:
		raise
		logger.warning("Error occurred while fetching search results")
	return results

