import yaml

def import_config(filename):
	with open(filename, 'r') as stream:
		config = yaml.load(stream)
	return config
