#!/usr/bin/env python3

import argparse
import os.path
from medialinkfs import organize
import logging

logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser(description="Organize a media library using symlinks")
parser.add_argument('--config', '-c', action='store', dest='config', required=True)
parser.add_argument('--ignore-cache', '-i', action='store_true', dest='ignore_cache')
parser.add_argument('--verbose', '-v')
parser.add_argument('set_name', nargs='?')
options = vars(parser.parse_args())

if not os.path.isfile(options['config']):
	print("Could not open config file %s"%options['config'])

organize.organize(options)
