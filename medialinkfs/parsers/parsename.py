API_BASE = 'http://vgmdb.info/'
MATCH_THRESHOLD = 0.7

import os.path
import re
import logging

logger = logging.getLogger(__name__)

class Module(object):
	wrapped = lambda x: r'[^0-9a-zA-Z]%s([^0-9a-zA-Z])?'%(x,)
	yearmatcher = re.compile(wrapped('((19|20)[0-9][0-9])'))
	resmatcher = re.compile(wrapped('(240|288|320|480|576|720|1080|2160|4320|8640)(p|i)?'), re.IGNORECASE)
	formats = r'([hx]264|avc|xvid|divx)'
	scenematcher = re.compile(wrapped('%s[-_]([A-Za-z0-9]+)'%(formats,)), re.IGNORECASE)
	formatmatcher = re.compile(wrapped(formats), re.IGNORECASE)
	extmatcher = re.compile(r'\.([a-zA-Z0-9]{2,4})$')

	clean_doublespace = lambda x: x.replace('  ',' ')

	def __init__(self, parser_options):
		self.parser_options = parser_options

	@staticmethod
	def remove_wrapped_match(string, match):
		firsti = match.start()
		lasti = match.end()
		lastgroup = match.groups()[-1]
		first = string[firsti]
		if first in ['[','(','{'] and lastgroup:	# wrapped by matching symbols
			ret = string[:firsti] + string[lasti:]  # kill the closing brace
		elif lastgroup:
			ret = string[:firsti] + string[lasti-1:]   # no brace to remove
		else:
			ret = string[:firsti] + string[lasti:]   # no brace to remove, no string at the end to keep
		ret = Module.clean_doublespace(ret)
		ret = ret.strip()
		return ret

	def get_metadata(self, metadata):
		path = metadata['path']
		name = os.path.basename(path)
		name = Module.clean_doublespace(name)
		name = name.strip()
		logger.debug("Loading metadata for %s"%name)
		data = {}

		yearfound = Module.yearmatcher.search(name)
		if yearfound:
			data['year'] = int(yearfound.group(1))
			name = Module.remove_wrapped_match(name, yearfound)

		resfound = Module.resmatcher.search(name)
		if resfound:
			data['resolution'] = int(resfound.group(1))
			if resfound.group(2) in ['i','I']:
				data['interlaced'] = True
			name = Module.remove_wrapped_match(name, resfound)

		scenefound = Module.scenematcher.search(name)
		if scenefound:
			data['format'] = scenefound.group(1).lower()
			data['release_group'] = scenefound.group(2)
			name = Module.remove_wrapped_match(name, scenefound)

		formatfound = Module.formatmatcher.search(name)
		if formatfound:
			data['format'] = formatfound.group(1).lower()
			name = Module.remove_wrapped_match(name, formatfound)

		extfound = Module.extmatcher.search(name)
		if extfound:
			ext = extfound.group(1)
			if ext.lower() == ext or ext.upper() == ext:
				data['extension'] = ext
				name = Module.extmatcher.sub("", name)

		if name.count('.') > name.count(' '):
			# period-separated filename
			name = name.replace('.', ' ')
			name = Module.clean_doublespace(name)
			name = name.strip()

		data['name'] = name
		return data
