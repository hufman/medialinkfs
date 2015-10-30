from .config import import_config
from .deepmerge import deep_merge
from .parsers import load_parser
from . import errors
from . import metadata
from . import sourcelist
from . import output
import os
import os.path
import logging
import sys
import traceback
import shutil
import hashlib
import json
import glob
import re

try:
	import simplejson as json
except:
	pass

logger = logging.getLogger(__name__)

def organize(options):
	config = import_config(options['config'])
	for settings in config.sets():
		if options['set_name'] == None or options['set_name'] == settings['name']:
			organize_set(options, settings)

def fetch_set(options, settings):
	logger.info("Beginning to fetch metadata for %s"%(settings['name'],))
	processed_files = load_progress(settings)
	if len(processed_files) == 0:
		start_progress(settings)
	else:
		logger.info("Resuming progress after %s items"%(len(processed_files)))

	for name in sourcelist.items(settings):
		if name in processed_files:
			continue
		fetch_item_metadata(settings, name)
		add_progress(settings, name)
	finish_progress(settings)

def organize_set(options, settings):
	logger.info("Beginning to organize %s"%(settings['name'],))
	prepare_for_organization(settings)
	processed_files = load_progress(settings)
	if len(processed_files) == 0:
		start_progress(settings)
	else:
		logger.info("Resuming progress after %s items"%(len(processed_files)))

	for name in sourcelist.items(settings):
		if name in processed_files:
			continue
		organize_item(options, settings, name)
		add_progress(settings, name)
	finish_progress(settings)

def organize_item(options, settings, name):
	metadata = load_item_metadata(options, settings, name)
	output.do_output(options, settings, metadata)

def fetch_item_metadata(settings, name):
	fresh_metadata = metadata.fetch_item(settings, name)
	return fresh_metadata

def load_item_metadata(options, settings, name):
	logger.debug("Loading metadata for %s"%(name,))
	path = os.path.join(settings['sourceDir'], name)
	if not options.get('ignore_cache', False):	# if the user didn't say to ignore the cache
		cached_metadata = metadata.load_item(settings, name)
		if 'itemname' in cached_metadata:	# valid cached data
			return cached_metadata
	# manually ignoring cache, or doesn't have it cached
	return fetch_item_metadata(settings, name)

# Preparation
def prepare_for_organization(settings):
	all_parser_options = settings.get('parser_options', {})
	for parser_name in settings['parsers']:
		parser_options = all_parser_options.get(parser_name, {})
		parser = load_parser(parser_name, parser_options)
		if not parser:
			raise errors.MissingParser("Set %s can't load parser %s"%(settings['name'], parser_name))
	if not os.path.isdir(settings['sourceDir']):
		raise errors.MissingSourceDir("Set %s has an invalid sourceDir %s"%(settings['name'], settings['sourceDir']))
	if 'cacheDir' not in settings:
		settings['cacheDir'] = os.path.join(settings['sourceDir'], '.cache')
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
	allowed_deletions_patterns = ['.toc', '.toc-*', '.toc.*']
	allowed_deletions = []
	for pattern in allowed_deletions_patterns:
		found_deletions = glob.glob(os.path.join(path, pattern))
		trimmed_deletions = [x[len(path)+1:] for x in found_deletions]
		allowed_deletions.extend(trimmed_deletions)
	if '.toc.extra' in allowed_deletions:
		allowed_deletions.remove('.toc.extra')

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
	nametoc = os.path.join(path,'.toc-%s'%(settings['name'],))
	namedone = os.path.join(path,'.toc.done-%s'%(settings['name'],))
	nameold = os.path.join(path,'.toc.old-%s'%(settings['name'],))
	nameextra = os.path.join(path,'.toc.extra')
	if not os.path.isfile(nametoc):
		return

	# move around the old toc
	if os.path.isfile(nameold):
		os.unlink(nameold)
	if os.path.isfile(namedone):
		os.rename(namedone, nameold)

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
	proper_contents = []
	for alttoc in glob.glob(os.path.join(path, '.toc.done*')):
		with open(alttoc, 'r') as toc:
			proper_contents.extend([x.strip() for x in toc.readlines() if x.strip()!=''])
	with open(nametoc, 'r') as toc:
		proper_contents.extend([x.strip() for x in toc.readlines() if x.strip()!=''])

	# start deleting stuff
	for name in os.listdir(path):
		if name[:4] == '.toc':
			continue
		subpath = os.path.join(path,name)
		if subpath not in extra_paths and \
		   name not in proper_contents and \
		   name not in extra_contents:
			if not (settings.get('fakeclean', False)):
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

	# declare this toc done
	os.rename(nametoc, namedone)

