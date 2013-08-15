import yaml

def import_config(filename):
	stream = open(filename, 'r')
	config = yaml.load(stream)
	return config
