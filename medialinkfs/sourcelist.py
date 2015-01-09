import os
import os.path
import re

def items(settings):
	regex = None
	if 'regex' in settings:
		regex = re.compile(settings['regex'])
	omitted_dirs = _generate_omitted_dirs(settings)
	files = os.listdir(settings['sourceDir'])
	files = sorted(files)
	if settings['scanMode'] in ['directories', 'files', 'toplevel']:
		for name in files:
			path = os.path.join(settings['sourceDir'], name)
			if path in omitted_dirs:
				continue
			if settings['scanMode'] != 'toplevel':
				if settings['scanMode'] == 'directories' and \
				   not os.path.isdir(path):
					continue
				if settings['scanMode'] == 'files' and \
				   not os.path.isfile(path):
					continue
			if regex and not regex.search(path):
				continue
			yield name

def _generate_omitted_dirs(settings):
	dirs = []
	dirs.append(os.path.join(settings['cacheDir']))
	dirs.extend([o['dest'] for o in settings['output']])
	return dirs

