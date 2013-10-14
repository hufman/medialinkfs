from .config import import_config
from .parsers import load_parser
from .deepmerge import deep_merge
from . import errors
import os
import os.path
import logging
import sys
import traceback
import shutil
import hashlib
import json
import glob

try:
	import simplejson as json
except:
	pass

logger = logging.getLogger(__name__)

def organize(options):
	config = import_config(options['config'])
	for settings in config['sets']:
		if options['set_name'] == None or options['set_name'] == settings['name']:
			organize_set(options, settings)

def organize_set(options, settings):
	logger.info("Beginning to organize %s"%(settings['name'],))
	prepare_for_organization(settings)
	processed_files = load_progress(settings)
	if len(processed_files) == 0:
		start_progress(settings)
	else:
		logger.info("Resuming progress after %s items"%(len(processed_files)))

	omitted_dirs = generate_omitted_dirs(settings)
	files = os.listdir(settings['sourceDir'])
	files = sorted(files)
	if settings['scanMode'] == 'directories':
		for name in files:
			if name in processed_files:
				continue
			if os.path.join(settings['sourceDir'], name) in omitted_dirs:
				continue
			organize_item(options, settings, name)
			add_progress(settings, name)
	finish_progress(settings)

def organize_item(options, settings, name):
	metadata = load_item_metadata(options, settings, name)
	do_output(options, settings, metadata)

def load_item_metadata(options, settings, name):
	logger.debug("Loading metadata for %s"%(name,))
	path = os.path.join(settings['sourceDir'], name)
	if not ('ignore_cache' in options and options['ignore_cache']):
		cached_metadata = load_cached_metadata(settings, name)
	if 'name' in cached_metadata:	# valid cached data
		if 'preferCachedData' in settings and \
		   settings['preferCachedData']:
			logger.debug("Preferring cached data for %s"%(name,))
			return cached_metadata
		else:
			logger.debug("Loaded cached data for %s"%(name,))
	new_metadata = {"name":name, "path":path}
	for parser_name in settings['parsers']:
		parser = load_parser(parser_name)
		try:
			item_metadata = parser.get_metadata(path)
			if item_metadata == None:
				log_unknown_item(settings['cacheDir'], parser_name, name)
				continue
		except KeyboardInterrupt:
			raise
		except:
			log_crashed_parser(settings['cacheDir'], parser_name, name)
			continue
		deep_merge(new_metadata, item_metadata)
	
	metadata = cached_metadata
	metadata.update(new_metadata)
	save_cached_metadata(settings, metadata)
	return metadata

# Cache system
def get_cache_key(name):
	h = hashlib.new('md5')
	h.update(name.encode('utf-8'))
	return h.hexdigest()

def get_cache_path(settings, name):
	cache_key = get_cache_key(name)
	cache_dir = settings['cacheDir']
	cache_path = "%s/.cache-%s"%(cache_dir, cache_key)
	return cache_path

def load_cached_metadata(settings, name):
	""" Loads up any previously cached dat
	Returns {} if no data could be loaded
	"""
	cache_path = get_cache_path(settings, name)
	try:
		with open(cache_path) as reading:
			data = reading.read()
			return json.loads(data)
	except:
		if os.path.isfile(cache_path):
			msg = "Failed to open cache file for %s (%s): %s" % \
			      (name, cache_path, traceback.format_exc())
			logger.warning(msg)
		return {}

def save_cached_metadata(settings, data):
	cache_path = get_cache_path(settings, data['name'])
	try:
		with open(cache_path, 'w') as writing:
			writing.write(json.dumps(data))
	except:
		msg = "Failed to save cache file for %s (%s): %s" % \
		      (data['name'], cache_path, traceback.format_exc())
		logger.warning(msg)

# Actual organizing
def do_output(options, settings, metadata):
	for group in settings['output']:
		dest = group['dest']
		groupBy = group['groupBy']
		logger.debug("Sorting %s by %s"%(metadata['name'],group['groupBy']))
		if not groupBy in metadata:
			continue
		value = metadata[groupBy]
		if isinstance(value,str):
			values = [value]
		else:
			values = value
		for value in values:
			value = value.replace('/','／')
			logger.debug("Putting %s into %s"%(metadata['name'],value))
			valueDir = os.path.join(dest, value)
			if not os.path.isdir(valueDir):
				os.mkdir(valueDir)
			with open(os.path.join(dest, '.toc'), 'a') as toc:
				toc.write("%s\n"%(value,))
			destpath = os.path.join(valueDir, metadata['name'])
			link = os.path.relpath(metadata['path'], valueDir)
			if os.path.islink(destpath) and \
			   os.readlink(destpath) != link:
				os.unlink(destpath)
			if not os.path.islink(destpath):
				os.symlink(link, destpath)
			with open(os.path.join(valueDir, '.toc'), 'a') as toc:
				toc.write("%s\n"%(metadata['name'],))

# Preparation
def prepare_for_organization(settings):
	for parser_name in settings['parsers']:
		parser = load_parser(parser_name)
		if not parser:
			raise errors.MissingParser("Set %s can't load parser %s"%(settings['name'], parser_name))
	if not os.path.isdir(settings['sourceDir']):
		raise errors.MissingSourceDir("Set %s has an invalid sourceDir %s"%(settings['name'], settings['sourceDir']))
	prepare_cache_dir(settings['cacheDir'])

	if 'output' in settings:
		for output_dir in settings['output']:
			if not os.path.isdir(output_dir['dest']):
				raise errors.MissingDestDir("Set %s is missing an output directory %s"%(settings['name'], output_dir['dest']))

def prepare_cache_dir(cache_dir):
	join = os.path.join
	dirs = [cache_dir]
	for d in dirs:
		if not os.path.isdir(d):
			os.mkdir(d)

def generate_omitted_dirs(settings):
	dirs = []
	dirs.append(os.path.join(settings['cacheDir']))
	dirs.extend([o['dest'] for o in settings['output']])
	return dirs

# Progress tracking
def load_progress(settings):
	progress_filename = os.path.join(settings['cacheDir'], 'progress')
	if os.path.isfile(progress_filename):
		progress_file = open(progress_filename,'r')
		return [x.strip() for x in progress_file.readlines() if x.strip()!='']
	return []

def start_progress(settings):
	failed = os.path.join(settings['cacheDir'], 'failed.log')
	if os.path.isfile(failed):
		os.unlink(failed)
	unknown = os.path.join(settings['cacheDir'], 'unknown.log')
	if os.path.isfile(unknown):
		os.unlink(unknown)

def add_progress(settings, name):
	progress_filename = os.path.join(settings['cacheDir'], 'progress')
	with open(progress_filename,'a') as progress_file:
		progress_file.write("%s\n"%(name,))

def finish_progress(settings):
	if not ('noclean' in settings and settings['noclean']):
		cleanup_extra_output(settings)
	progress_filename = os.path.join(settings['cacheDir'], 'progress')
	if os.path.isfile(progress_filename):
		os.unlink(progress_filename)

# Finishing up and cleaning
def cleanup_extra_output(settings):
	logger.info("Cleaning up old files")
	for output in settings['output']:
		cleanup_extra_toc(settings, output['dest'], recurse_levels=1)

def safe_delete_dir(path):
	# Extra files that we are allowed to delete
	allowed_deletions_patterns = ['.toc.*']
	allowed_deletions = []
	for pattern in allowed_deletions_patterns:
		found_deletions = glob.glob(os.path.join(path, pattern))
		trimmed_deletions = [x[len(path)+1:] for x in found_deletions]
		allowed_deletions.extend(trimmed_deletions)

	# load up the list of extra things that we should not delete
	nameextra = os.path.join(path,'.toc.extra')
	extra_contents = []
	try:
		with open(nameextra) as extra:
			extra_contents = [x.strip() for x in extra.readlines()
			                  if x.strip()!='']
	except:
		pass

	# start unlinking things
	for name in os.listdir(path):
		if name in extra_contents:
			continue
		spath = os.path.join(path, name)
		try:
			if not os.path.islink(spath) and \
			   os.path.isdir(spath):
				safe_delete_dir(spath)
			if not os.path.islink(spath) and \
			   os.path.isfile(spath):
				if name in allowed_deletions:
					os.unlink(spath)
			if os.path.islink(spath):
				os.unlink(spath)
		except:
			raise
			msg = "An error happened while safely cleaning %s: %s" % \
			      (spath, traceback.format_exc())
			logger.warning(msg)

	if len(os.listdir(path)) == 0:
		os.rmdir(path)

def cleanup_extra_toc(settings, path, recurse_levels = 1):
	nametoc = os.path.join(path,'.toc')
	namedone = os.path.join(path,'.toc.done')
	nameold = os.path.join(path,'.toc.old')
	nameextra = os.path.join(path,'.toc.extra')
	if not os.path.isfile(nametoc):
		return

	# any other elements that are manually excepted
	extra_contents = []
	try:
		with open(nameextra, 'r') as extra:
			extra_contents = [x.strip() for x in extra.readlines()
			                  if x.strip()!='']
	except:
		pass

	# any other directories we need, and should not delete
	extra_paths = []
	extra_paths.append(settings['sourceDir'])
	extra_paths.append(settings['cacheDir'])
	extra_paths.extend([o['dest'] for o in settings['output']])

	# load the list of proper files in this dir
	with open(nametoc, 'r') as toc:
		proper_contents = [x.strip() for x in toc.readlines() if x.strip()!='']

	# start deleting stuff
	for name in os.listdir(path):
		if name[:4] == '.toc':
			continue
		subpath = os.path.join(path,name)
		if subpath not in extra_paths and \
		   name not in proper_contents and \
		   name not in extra_contents:
			if not ('fakeclean' in settings and
				settings['fakeclean']):
				if not os.path.islink(subpath) and \
				   os.path.isdir(subpath):
					logger.debug("Removing extra dir %s"%(subpath,))
					safe_delete_dir(subpath)
				elif os.path.islink(subpath):
					logger.debug("Removing extra link %s"%(subpath,))
					os.unlink(subpath)
				else:
					logger.debug("Not removing extra file %s"%(subpath,))
			else:
				if not os.path.islink(subpath) and \
				   os.path.isdir(subpath):
					logger.debug("Would remove extra dir %s"%(subpath,))
				elif os.path.islink(subpath):
					logger.debug("Would remove extra file %s"%(subpath,))
				else:
					logger.debug("Would not remove extra file %s"%(subpath,))
		else:
			if os.path.isdir(subpath) and recurse_levels > 0:
				cleanup_extra_toc(settings, subpath, recurse_levels - 1)
			else:
				pass
	if os.path.isfile(nameold):
		os.unlink(nameold)
	if os.path.isfile(namedone):
		os.rename(namedone, nameold)
	os.rename(nametoc, namedone)

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
