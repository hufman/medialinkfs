# Responsible for loading an item's metadata
from . import cache
from .deepmerge import deep_merge
from .parsers import load_parser
import logging
import os.path
import re
import traceback

logger = logging.getLogger(__name__)

def load_item(settings, name):
	logger.debug("Loading metadata for %s from cache"%(name,))
	cached_metadata = cache.load(settings, name)
	return cached_metadata

def fetch_item(settings, name):
	logger.debug("Fetching metadata for %s"%(name,))
	path = os.path.join(settings['sourceDir'], name)
	new_metadata = {"itemname":name, "path":path}
	for parser_name in settings['parsers']:
		all_parser_options = settings.get('parser_options', {})
		parser_options = all_parser_options.get(parser_name, {})
		parser = load_parser(parser_name, parser_options)
		try:
			item_metadata = parser.get_metadata(dict(new_metadata))
			if item_metadata == None:
				log_unknown_item(settings['cacheDir'], parser_name, name)
				continue
		except KeyboardInterrupt:
			raise
		except:
			log_crashed_parser(settings['cacheDir'], parser_name, name)
			continue
		deep_merge(new_metadata, item_metadata)
	cache.save(settings, new_metadata)
	return new_metadata

# Logging
def log_unknown_item(cache_dir, parser_name, item_name):
	logger.warning("%s couldn't locate %s"%(parser_name, item_name))
	with open(os.path.join(cache_dir, "unknown.log"), 'a') as log:
		log.write("%s couldn't locate %s\n"%(parser_name, item_name))

def log_crashed_parser(cache_dir, parser_name, item_name):
	message = "%s crashed while parsing %s:\n%s"%(parser_name, item_name, traceback.format_exc())
	logger.error(message)
	with open(os.path.join(cache_dir, "failed.log"), 'a') as log:
		log.write(message+"\n")
