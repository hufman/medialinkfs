import os
import os.path
import difflib
import re
import logging
import stagger
from numbers import Number

from medialinkfs.deepmerge import deep_merge

logger = logging.getLogger(__name__)

class Module(object):
	def __init__(self, parser_options):
		self.parser_options = parser_options

	def get_metadata(self, metadata):
		path = metadata['path']
		name = os.path.basename(path)
		logger.debug("Loading metadata for %s"%name)

		data = {}
		if os.path.isdir(path):
			data = self.load_dir(path)
		if os.path.isfile(path):
			data = self.load_id3(path)
		if data == {}:
			logger.debug("Found no metadata for %s"%name)
			return None	# couldn't find a match

		return data

	def load_dir(self, path):
		data = {}
		for name in os.listdir(path):
			subpath = os.path.join(path, name)
			if os.path.isdir(subpath):
				deep_merge(data, self.load_dir(subpath))
			if os.path.isfile(subpath):
				deep_merge(data, self.load_id3(subpath))
		return data

	def load_id3(self, path):
		data = {}
		keys = ['album', 'album_artist', 'artist', 'composer', 'genre',
			'sort_album', 'sort_album_artist', 'sort_artist',
			'sort_composer', 'sort_title', 'title',
			'track_total', 'date'
		]
		multikeys = {
		   'album': 'albums',
		   'album_artist': 'artists',
		   'artist': 'artists',
		   'composer': 'composers',
		   'genre': 'genres',
		   'sort_album': 'albums',
		   'sort_album_artist': 'artists',
		   'sort_artist': 'artists',
		   'sort_composer': 'composers'
		}
		tag = stagger.read_tag(path)
		for key in keys:
			if not hasattr(tag, key):
				continue
			obj = getattr(tag, key)
			if isinstance(obj, Number) or \
			   (isinstance(obj, str) and \
			   len(obj) > 0):
				data[key] = obj
				if key in multikeys:
					mkey = multikeys[key]
					if mkey not in data:
						data[mkey] = []
					if obj not in data[mkey]:
						data[mkey].append(obj)
		return data
