# Loads or saves an item's metadata
import json
import hashlib
import logging
import os.path

try:
	import simplejson as json
except:
	pass

logger = logging.getLogger(__name__)

def get_cache_key(name):
	h = hashlib.new('md5')
	h.update(name.encode('utf-8'))
	return h.hexdigest()

def get_cache_path(settings, name):
	cache_key = get_cache_key(name)
	cache_dir = settings['cacheDir']
	cache_path = "%s/.cache-%s"%(cache_dir, cache_key)
	return cache_path

def add_validation_cookies(settings, data):
	""" Before saving data to disk, add settings to validate the cache later """
	data['_source'] = {}
	for key in ['parsers', 'parser_options']:
		if key in settings:
			data['_source'][key] = settings[key]
	return data

def check_validation_cookies(settings, data):
	""" Check that the current settings would still generate this cache item """
	for key in ['parsers', 'parser_options']:
		if '_source' in data and \
		   key in data['_source'] and \
		   data['_source'][key] != settings[key]:
			return False
	return True

def strip_validation_cookies(data):
	""" Delete the validation information for returning to the client """
	if '_source' in data:
		del data['_source']
	return data

def load(settings, name):
	""" Loads up any previously cached dat
	Returns {} if no data could be loaded
	"""
	cache_path = get_cache_path(settings, name)
	try:
		with open(cache_path) as reading:
			data = reading.read()
			parsed_data = json.loads(data)
			# check that the cache's parser_options are the same
			valid = check_validation_cookies(settings, parsed_data)
			if not valid:
				logger.debug("Cache for %s was created with different parser options" % (name,))
				return {}
			parsed_data = strip_validation_cookies(parsed_data)
			return parsed_data
	except Exception as e:
		if os.path.isfile(cache_path):
			msg = "Failed to open cache file for %s (%s): %s" % \
			      (name, cache_path, e)
			logger.warning(msg)
		logger.debug("No cache file found for %s (%s)" % (name, cache_path))
		return {}

def save(settings, data):
	cache_path = get_cache_path(settings, data['itemname'])
	data = add_validation_cookies(settings, data)
	try:
		with open(cache_path, 'w') as writing:
			writing.write(json.dumps(data))
	except:
		msg = "Failed to save cache file for %s (%s): %s" % \
		      (data['itemname'], cache_path, traceback.format_exc())
		logger.warning(msg)

