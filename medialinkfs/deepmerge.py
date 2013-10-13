# Code to deeply merge two objects together
def deep_merge(target, update):
	if hasattr(target, 'update') and \
	   hasattr(update, '__getitem__'):
		deep_merge_dict(target, update)
	elif hasattr(target, '__iter__') and \
	     hasattr(update, '__iter__'):
		deep_merge_list(target, update)
	return target

def deep_merge_dict(target, update):
	for skey, svalue in update.items():
		if skey in target:
			if hasattr(target[skey], 'update') and \
			   hasattr(update[skey], '__getitem__'):
				deep_merge_dict(target[skey], update[skey])
			elif hasattr(target[skey], 'append') and \
			     hasattr(update[skey], '__iter__'):
				deep_merge_list(target[skey], update[skey])
			else:
				target[skey] = update[skey]
		else:
			target[skey] = update[skey]

def deep_merge_list(target, update):
	for item in update:
		if item not in target:
			target.append(item)

