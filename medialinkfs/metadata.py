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
	""" A smart object to combine metadata from several plugins """
	def __init__(self):
		self.metadata = {}
		self.sources = []
		self.view = {}

	# Add a new set of data to this metadata
	def add_source(self, name, metadata):
		""" Adds a new source of metadata, and update the view """
		self._add_source(name, metadata)
		self._update_view(name)

	def _add_source(self, name, metadata):
		""" Adds a new source of metadata, without updating the view """
		self.sources.append(name)
		self.metadata[name] = metadata

	# Maintain the simple key access data
	def _rebuild_view(self):
		""" Rebuild the metadata view from empty """
		self.view.clear()
		for name in self.sources:
			self._update_view(name)

	def _update_view(self, name):
		""" Merge in a new metadata plugin to the view """
		deep_merge(self.view, self.metadata[name])

	# Standard key access
	def __contains__(self, key):
		return self.view.__contains__(key)
	def __getitem__(self, key):
		return self.view.__getitem__(key)
	def __iter__(self):
		return self.view.__iter__()
	def __len__(self):
		return self.view.__len__()
	def get(self, key, default=None):
		return self.view.get(key, default)
	def keys(self):
		return self.view.keys()
	def items(self):
		return self.view.items()
	def values(self):
		return self.view.values()

	# Cache serialization
	def serialize(self):
		""" Save this object to be stored to cache """
		return {'sources': self.sources,
		        'metadata': self.metadata,
		        'itemname': self['itemname']}
	@staticmethod
	def deserialize(serialized):
		""" Loads a metadata object from a cache serialization """
		order = serialized.get('order', [])
		raw_metadata = serialized.get('metadata', {})
		metadata = Metadata()
		for name in serialized.get('sources', []):
			metadata._add_source(name, raw_metadata.get(name, {}))
		metadata._rebuild_view()
		return metadata


class MetadataLoader(object):
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
		serialized_metadata = self.cache.load(name)
		cached_metadata = Metadata.deserialize(serialized_metadata)
		return cached_metadata

	def fetch_item(self, path, name):
		logger.debug("Fetching metadata for %s"%(name,))
		new_metadata = Metadata()
		new_metadata.add_source('name', {"itemname":name, "path":path})
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
			new_metadata.add_source(parser_name, item_metadata)
		self.cache.save(new_metadata.serialize())
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
