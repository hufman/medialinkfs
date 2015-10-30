import importlib
def load_parser(parser_name, parser_options):
	# strip off aliases
	parser_name = parser_name.split('.')[0]
	# load the module
	module = importlib.import_module('.'+parser_name, 'medialinkfs.parsers')
	# instantiate the module with the options
	return module.Module(parser_options)
