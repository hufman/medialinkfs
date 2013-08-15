import importlib
def load_parser(parser_name):
	return importlib.import_module('.'+parser_name, 'medialinkfs.parsers')
