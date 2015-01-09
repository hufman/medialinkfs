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

def load(settings, name):
	""" Loads up any previously cached dat
	Returns {} if no data could be loaded
	"""
	cache_path = get_cache_path(settings, name)
	if 'parser_options' in settings:
		parser_options = json.dumps(settings['parser_options'])
	else:
		parser_options = None
	try:
		with open(cache_path) as reading:
			data = reading.read()
			parsed_data = json.loads(data)
			# check that th cache's parser_options are the same
			if 'parser_options' in parsed_data and \
			   parsed_data['parser_options'] != parser_options:
				return {}
			if 'parser_options' in parsed_data:
				del parsed_data['parser_options']
			return parsed_data
	except:
		if os.path.isfile(cache_path):
			msg = "Failed to open cache file for %s (%s): %s" % \
			      (name, cache_path)
			logger.warning(msg)
		return {}

def save(settings, data):
	cache_path = get_cache_path(settings, data['itemname'])
	if 'parser_options' in settings:
		data['parser_options'] = settings['parser_options']
	try:
		with open(cache_path, 'w') as writing:
			writing.write(json.dumps(data))
	except:
		msg = "Failed to save cache file for %s (%s): %s" % \
		      (data['itemname'], cache_path, traceback.format_exc())
		logger.warning(msg)

