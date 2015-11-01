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

class Cache(object):
	def __init__(self, settings):
		self.settings = settings

	def get_cache_key(self, name):
		h = hashlib.new('md5')
		h.update(name.encode('utf-8'))
		return h.hexdigest()

	def get_cache_path(self, name):
		cache_key = self.get_cache_key(name)
		cache_dir = self.settings['cacheDir']
		cache_path = "%s/.cache-%s"%(cache_dir, cache_key)
		return cache_path

	def add_validation_cookies(self, data):
		""" Before saving data to disk, add settings to validate the cache later """
		data['_source'] = {}
		for key in ['parsers', 'parser_options']:
			if key in self.settings:
				data['_source'][key] = self.settings[key]
		return data

	def check_validation_cookies(self, data):
		""" Check that the current settings would still generate this cache item """
		for key in ['parsers', 'parser_options']:
			if '_source' in data and \
			   key in data['_source'] and \
			   data['_source'][key] != self.settings[key]:
				return False
		return True

	def strip_validation_cookies(self, data):
		""" Delete the validation information for returning to the client """
		if '_source' in data:
			del data['_source']
		return data

	def load(self, name):
		""" Loads up any previously cached dat
		Returns {} if no data could be loaded
		"""
		cache_path = self.get_cache_path(name)
		try:
			with open(cache_path) as reading:
				data = reading.read()
				parsed_data = json.loads(data)
				# check that the cache's parser_options are the same
				valid = self.check_validation_cookies(parsed_data)
				if not valid:
					logger.debug("Cache for %s was created with different parser options" % (name,))
					return {}
				parsed_data = self.strip_validation_cookies(parsed_data)
				return parsed_data
		except Exception as e:
			if os.path.isfile(cache_path):
				msg = "Failed to open cache file for %s (%s): %s" % \
				      (name, cache_path, e)
				logger.warning(msg)
			logger.debug("No cache file found for %s (%s)" % (name, cache_path))
			return {}

	def save(self, data):
		cache_path = self.get_cache_path(data['itemname'])
		data = self.add_validation_cookies(data)
		try:
			with open(cache_path, 'w') as writing:
				writing.write(json.dumps(data))
		except:
			msg = "Failed to save cache file for %s (%s): %s" % \
			      (data['itemname'], cache_path, traceback.format_exc())
			logger.warning(msg)

