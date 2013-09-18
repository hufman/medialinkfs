from .config import import_config
from .parsers import load_parser
from . import errors
import os
import os.path
import logging
import sys
import traceback
import shutil

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
	metadata = {"name":name, "path":path}
	for parser_name in settings['parsers']:
		parser = load_parser(parser_name)
		try:
			new_metadata = parser.get_metadata(path)
			if new_metadata == None:
				log_unknown_item(settings['cacheDir'], parser_name, name)
				continue
		except KeyboardInterrupt:
			raise
		except:
			log_crashed_parser(settings['cacheDir'], parser_name, name)
			continue
		metadata.update(new_metadata)
	return metadata

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
	cleanup_extra_output(settings)
	progress_filename = os.path.join(settings['cacheDir'], 'progress')
	if os.path.isfile(progress_filename):
		os.unlink(progress_filename)

def cleanup_extra_output(settings):
	logger.info("Cleaning up old files")
	for output in settings['output']:
		cleanup_extra_toc(output['dest'], recurse_levels=1)

def cleanup_extra_toc(path, recurse_levels = 1):
	nametoc = os.path.join(path,'.toc')
	namedone = os.path.join(path,'.toc.done')
	nameold = os.path.join(path,'.toc.old')
	if not os.path.isfile(nametoc):
		return
	with open(nametoc, 'r') as toc:
		proper_contents = [x.strip() for x in toc.readlines() if x.strip()!='']
		for name in os.listdir(path):
			if name[:4] == '.toc':
				continue
			subpath = os.path.join(path,name)
			if name not in proper_contents:
				if not os.path.islink(subpath) and \
				   os.path.isdir(subpath):
					logger.debug("Removing extra dir %s"%(subpath,))
					shutil.rmtree(subpath, ignore_errors=True)
				else:
					logger.debug("Removing extra file %s"%(subpath,))
					os.unlink(subpath)
			else:
				if os.path.isdir(subpath) and recurse_levels > 0:
					cleanup_extra_toc(subpath, recurse_levels - 1)
				else:
					pass
	if os.path.isfile(nameold):
		os.unlink(nameold)
	if os.path.isfile(namedone):
		os.rename(namedone, nameold)
	os.rename(nametoc, namedone)

def log_unknown_item(cache_dir, parser_name, item_name):
	logger.warning("%s couldn't locate %s"%(parser_name, item_name))
	with open(os.path.join(cache_dir, "unknown.log"), 'a') as log:
		log.write("%s couldn't locate %s\n"%(parser_name, item_name))

def log_crashed_parser(cache_dir, parser_name, item_name):
	message = "%s crashed while parsing %s:\n%s"%(parser_name, item_name, traceback.format_exc())
	logger.error(message)
	with open(os.path.join(cache_dir, "failed.log"), 'a') as log:
		log.write(message+"\n")
