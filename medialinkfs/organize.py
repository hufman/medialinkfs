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
			organizer = OrganizeSet(options, settings)
			organizer.process_all()

class OrganizeSet(object):
	def __init__(self, options, settings):
		self.options = options
		self.settings = settings
		self.source_list = sourcelist.SourceItems(self.settings)
		self.source_dir = self.source_list.get_source_dir()
		self.validate_settings()
		self.metadata = metadata.MetadataLoader(settings)
		self.cache_dir = self.metadata.cache.get_cache_dir()

	def fetch_set(self):
		logger.info("Beginning to fetch metadata for %s"%(self.settings['name'],))
		processed_files = self.load_progress()
		if len(processed_files) == 0:
			self.start_progress()
		else:
			logger.info("Resuming progress after %s items"%(len(processed_files)))

		for name in self.source_list:
			if name in processed_files:
				continue
			self.fetch_item_metadata(name)
			self.add_progress(name)
		self.finish_progress()

	def process_all(self):
		logger.info("Beginning to organize %s"%(self.settings['name'],))
		self.prepare_for_organization()
		processed_files = self.load_progress()
		if len(processed_files) == 0:
			self.start_progress()
		else:
			logger.info("Resuming progress after %s items"%(len(processed_files)))

		for name in self.source_list:
			if name in processed_files:
				continue
			self.organize_item(name)
			self.add_progress(name)
		self.finish_progress()

	def organize_item(self, name):
		metadata = self.load_item_metadata(name)
		output.do_output(self.options, self.settings, metadata)

	def fetch_item_metadata(self, name):
		path = os.path.join(self.source_dir, name)
		fresh_metadata = self.metadata.fetch_item(path, name)
		return fresh_metadata

	def load_item_metadata(self, name):
		logger.debug("Loading metadata for %s"%(name,))
		if not self.options.get('ignore_cache', False):	# if the user didn't say to ignore the cache
			cached_metadata = self.metadata.load_item(name)
			if 'itemname' in cached_metadata:	# valid cached data
				return cached_metadata
		# manually ignoring cache, or doesn't have it cached
		return self.fetch_item_metadata(name)

	# Preparation
	def validate_settings(self):
		# check for parser and try to instantiate it
		all_parser_options = self.settings.get('parser_options', {})
		for parser_name in self.settings['parsers']:
			parser_options = all_parser_options.get(parser_name, {})
			parser = load_parser(parser_name, parser_options)
			if not parser:
				raise errors.MissingParser("Set %s can't load parser %s"%(self.settings['name'], parser_name))
		# check that we have a source dir
		if not os.path.isdir(self.source_dir):
			raise errors.MissingSourceDir("Set %s has an invalid sourceDir %s"%(self.settings['name'], self.source_dir))
		if 'cache_dir' not in self.settings:
			self.settings['cache_dir'] = os.path.join(self.source_dir, '.cache')
		# check that we have an output dir
		if 'output' in self.settings:
			for output_dir in self.settings['output']:
				if not os.path.isdir(output_dir['dest']):
					raise errors.MissingDestDir("Set %s is missing an output directory %s"%(self.settings['name'], output_dir['dest']))

	def prepare_for_organization(self):
		OrganizeSet.prepare_cache_dir(self.cache_dir)

	@staticmethod
	def prepare_cache_dir(cache_dir):
		join = os.path.join
		dirs = [cache_dir]
		for d in dirs:
			if not os.path.isdir(d):
				os.mkdir(d)

	# Progress tracking
	def load_progress(self):
		progress_filename = os.path.join(self.cache_dir, 'progress')
		if os.path.isfile(progress_filename):
			progress_file = open(progress_filename,'r')
			return [x.strip() for x in progress_file.readlines() if x.strip()!='']
		return []

	def start_progress(self):
		failed = os.path.join(self.cache_dir, 'failed.log')
		if os.path.isfile(failed):
			os.unlink(failed)
		unknown = os.path.join(self.cache_dir, 'unknown.log')
		if os.path.isfile(unknown):
			os.unlink(unknown)

	def add_progress(self, name):
		progress_filename = os.path.join(self.cache_dir, 'progress')
		with open(progress_filename,'a') as progress_file:
			progress_file.write("%s\n"%(name,))

	def finish_progress(self):
		if not ('noclean' in self.settings and self.settings['noclean']):
			self.cleanup_extra_output()
		progress_filename = os.path.join(self.cache_dir, 'progress')
		if os.path.isfile(progress_filename):
			os.unlink(progress_filename)

	# Finishing up and cleaning
	def cleanup_extra_output(self):
		logger.info("Cleaning up old files")
		for output in self.settings['output']:
			self.cleanup_extra_toc(output['dest'], recurse_levels=1)

	@staticmethod
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

	def cleanup_extra_toc(self, path, recurse_levels = 1):
		nametoc = os.path.join(path,'.toc-%s'%(self.settings['name'],))
		namedone = os.path.join(path,'.toc.done-%s'%(self.settings['name'],))
		nameold = os.path.join(path,'.toc.old-%s'%(self.settings['name'],))
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
		extra_paths.append(self.source_dir)
		extra_paths.append(self.cache_dir)
		extra_paths.extend([o['dest'] for o in self.settings['output']])

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
				if not (self.settings.get('fakeclean', False)):
					if not os.path.islink(subpath) and \
					   os.path.isdir(subpath):
						logger.debug("Removing extra dir %s"%(subpath,))
						OrganizeSet.safe_delete_dir(subpath)
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
					self.cleanup_extra_toc(subpath, recurse_levels - 1)
				else:
					pass

		# declare this toc done
		os.rename(nametoc, namedone)

