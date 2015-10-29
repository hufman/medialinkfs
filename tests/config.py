# -*- coding: UTF-8 -*-
import os
import tempfile
import shutil
import unittest

import logging
logging.basicConfig(level=logging.DEBUG, filename='tests.log')

import medialinkfs
import medialinkfs.config as config

base = os.path.dirname(__file__)

class TestConfig(unittest.TestCase):
	def setUp(self):
		logging.debug("Initializing unittest %s"%(self.id(),))

	def test_raw(self):
		c = config.Config({"test":True})
		self.assertEqual(True, c['test'])

	def test_sets_empty(self):
		c = config.Config({'test':True})
		self.assertEqual([], c.sets())

	def test_sets(self):
		c = config.Config({"sets":[{"thing":True}]})
		self.assertEqual(1, len(c.sets()))
		self.assertEqual(config.ConfigSet, type(c.sets()[0]))
