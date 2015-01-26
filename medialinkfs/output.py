import logging
import os
import os.path

logger = logging.getLogger(__name__)

def get_output_links(options, settings, metadata):
	""" Given an item's metadata and the settings
	    yield a series of (link, target) tuples
	    Link will be a full path to the organized path
	    Target will be the full path of the item
	"""
	itemname = metadata['itemname']
	itempath = metadata['path']
	for group in settings['output']:
		destdir = group['dest']
		if isinstance(group['groupBy'], str):
			groupsBy = [group['groupBy']]
		else:
			groupsBy = group['groupBy']
		for groupBy in groupsBy:
			if not groupBy in metadata:
				continue
			value = metadata[groupBy]
			if isinstance(value,str):
				values = [value]
			else:
				values = value
			for value in sorted(set(values)):
				if value == None:
					continue
				# clean up the directory name
				value = value.replace('/','／')
				# construct the full directory name
				valueDir = os.path.join(destdir, value)
				# construct the full symlink path
				destpath = os.path.join(valueDir, itemname)
				yield (destpath, itempath)

# Actual organizing
def do_output(options, settings, metadata):
	for output in get_output_links(options, settings, metadata):
		setname = settings['name']
		do_output_single(setname, output[0], output[1])

def do_output_single(setname, destpath, itempath):
	""" Adds an item that links from destpath to itempath
	"""
	valueDir = os.path.dirname(destpath)  # the path of the groupby dir
	destdir = os.path.dirname(valueDir)  # the parent dir of multiple groupbys
	value = os.path.basename(valueDir)   # the groupby value
	itemname = os.path.basename(itempath)   # the bare name of the destination item
	logger.debug("Putting %s into %s"%(itemname,value))
	# make the parent directory of the link
	if not os.path.isdir(valueDir):
		os.mkdir(valueDir)
	with open(os.path.join(destdir, '.toc-%s'%(setname,)), 'a') as toc:
		toc.write("%s\n"%(value,))
	# make the symlink
	link = os.path.relpath(itempath, valueDir)
	if os.path.islink(destpath) and \
	   os.readlink(destpath) != link:
		os.unlink(destpath)
	if not os.path.islink(destpath):
		os.symlink(link, destpath)
	with open(os.path.join(valueDir, '.toc-%s'%(setname,)), 'a') as toc:
		toc.write("%s\n"%(itemname,))

