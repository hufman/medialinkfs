# Responsible for loading an item's metadata
from . import cache
from .deepmerge import deep_merge
from .parsers import load_parser
import logging
import os.path
import re
import traceback

logger = logging.getLogger(__name__)

class Metadata(object):
	def __init__(self, settings):
		self.settings = settings
		self.cache = cache.Cache(self.settings)
		self.cache_dir = self.cache.get_cache_dir()
		self.parsers = {}
		self.load_parsers()

	def load_parsers(self):
		""" Pre-load parser objects """
		for parser_name in self.settings['parsers']:
			all_parser_options = self.settings.get('parser_options', {})
			parser_options = all_parser_options.get(parser_name, {})
			parser = load_parser(parser_name, parser_options)
			self.parsers[parser_name] = parser

	def load_item(self, name):
		logger.debug("Loading metadata for %s from cache"%(name,))
		cached_metadata = self.cache.load(name)
		return cached_metadata

	def fetch_item(self, name):
		logger.debug("Fetching metadata for %s"%(name,))
		path = os.path.join(self.settings['sourceDir'], name)
		new_metadata = {"itemname":name, "path":path}
		for parser_name in self.settings['parsers']:
			parser = self.parsers[parser_name]
			try:
				item_metadata = parser.get_metadata(dict(new_metadata))
				if item_metadata == None:
					self.log_unknown_item(parser_name, name)
					continue
			except KeyboardInterrupt:
				raise
			except:
				self.log_crashed_parser(parser_name, name)
				continue
			deep_merge(new_metadata, item_metadata)
		self.cache.save(new_metadata)
		return new_metadata

	# Logging
	def log_unknown_item(self, parser_name, item_name):
		logger.warning("%s couldn't locate %s"%(parser_name, item_name))
		with open(os.path.join(self.cache_dir, "unknown.log"), 'a') as log:
			log.write("%s couldn't locate %s\n"%(parser_name, item_name))

	def log_crashed_parser(self, parser_name, item_name):
		message = "%s crashed while parsing %s:\n%s"%(parser_name, item_name, traceback.format_exc())
		logger.error(message)
		with open(os.path.join(self.cache_dir, "failed.log"), 'a') as log:
			log.write(message+"\n")
