import yaml
from . import deepmerge

class Config(dict):
	def __init__(self, config):
		dict.__init__(self, config)
	def sets(self):
		return [ConfigSet(s) for s in self['sets']]

class ConfigSet(dict):
	def __init__(self, settings, default_settings=None, override_settings=None):
		combined_settings = dict(default_settings or {})
		deepmerge.deep_merge(combined_settings, settings)
		deepmerge.deep_merge(combined_settings, override_settings or {})
		dict.__init__(self, combined_settings)

def import_config(filename):
	with open(filename, 'r') as stream:
		config = yaml.load(stream)
	return Config(config)
