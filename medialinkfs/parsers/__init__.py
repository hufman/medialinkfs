import importlib
def load_parser(parser_name, parser_options):
	module = importlib.import_module('.'+parser_name, 'medialinkfs.parsers')
	return module.Module(parser_options)
