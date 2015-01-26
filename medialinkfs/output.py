import logging
import os
import os.path

logger = logging.getLogger(__name__)

# Actual organizing
def do_output(options, settings, metadata):
	for group in settings['output']:
		destdir = group['dest']
		if isinstance(group['groupBy'], str):
			groupsBy = [group['groupBy']]
		else:
			groupsBy = group['groupBy']
		for groupBy in groupsBy:
			if not groupBy in metadata:
				continue
			do_output_group(settings['name'], destdir, metadata, groupBy)

def do_output_group(setname, destdir, metadata, groupBy):
	logger.debug("Sorting %s by %s"%(metadata['itemname'],groupBy))
	value = metadata[groupBy]
	if isinstance(value,str):
		values = [value]
	else:
		values = value
	for value in sorted(set(values)):
		if value == None:
			continue
		value = value.replace('/','／')
		do_output_single(destdir, setname, metadata['path'], metadata['itemname'], value)

def do_output_single(destdir, setname, itempath, itemname, value):
	""" Adds an item from the set into the collection named value
	Adds FF8 from Albums into collection named Nobuo Uematsu
	"""
	logger.debug("Putting %s into %s"%(itemname,value))
	valueDir = os.path.join(destdir, value)
	if not os.path.isdir(valueDir):
		os.mkdir(valueDir)
	with open(os.path.join(destdir, '.toc-%s'%(setname,)), 'a') as toc:
		toc.write("%s\n"%(value,))
	destpath = os.path.join(valueDir, itemname)
	link = os.path.relpath(itempath, valueDir)
	if os.path.islink(destpath) and \
	   os.readlink(destpath) != link:
		os.unlink(destpath)
	if not os.path.islink(destpath):
		os.symlink(link, destpath)
	with open(os.path.join(valueDir, '.toc-%s'%(setname,)), 'a') as toc:
		toc.write("%s\n"%(itemname,))

