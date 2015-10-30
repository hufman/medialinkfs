import os
import os.path
import re

class SourceItems(object):
	def __init__(self, settings):
		self.settings = settings
		self._cache = None

	def __iter__(self):
		return self._cached().__iter__()
	def __getitem__(self, key):
		return self._cached().__getitem__(key)

	def _cached(self):
		if self._cache is None:
			self._cache = self.load_items()
		return self._cache
	def load_items(self):
		regex = None
		if 'regex' in self.settings:
			regex = re.compile(self.settings['regex'])
		omitted_dirs = self._generate_omitted_dirs()
		files = os.listdir(self.settings['sourceDir'])
		files = sorted(files)
		if self.settings['scanMode'] in ['directories', 'files', 'toplevel']:
			for name in files:
				path = os.path.join(self.settings['sourceDir'], name)
				if path in omitted_dirs:
					continue
				if self.settings['scanMode'] != 'toplevel':
					if self.settings['scanMode'] == 'directories' and \
					   not os.path.isdir(path):
						continue
					if self.settings['scanMode'] == 'files' and \
					   not os.path.isfile(path):
						continue
				if regex and not regex.search(path):
					continue
				yield name

	def _generate_omitted_dirs(self):
		dirs = []
		dirs.append(os.path.join(self.settings['cacheDir']))
		dirs.extend([o['dest'] for o in self.settings['output']])
		return dirs

