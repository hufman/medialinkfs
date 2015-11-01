# -*- coding: UTF-8 -*-
import os
import tempfile
import shutil
import unittest

import logging
logging.basicConfig(level=logging.DEBUG, filename='tests.log')

import medialinkfs.parsers.myapifilms as myapifilms
import tests._utils as _utils

base = os.path.dirname(__file__)

myapifilms.DELAY = 0	# disable api delay

class Testmyapifilms(_utils.TestAPI):
	def setUp(self):
		super().setUp()
		logging.debug("Initializing unittest %s"%(self.id(),))
		self.parser = myapifilms.Module({})

	def test_goodwillhunting(self):
		res = self.parser.get_metadata({"path":"/Good Will Hunting (1997)"})
		self.assertNotEqual(None, res)
		self.assertEqual(1997, res['year'])
		self.assertEqual(8.3, res['rating'])
		self.assertIn('Matt Damon', res['actors'])

	def test_goodwillhunting_wrongyear_doesnotexist(self):
		res = self.parser.get_metadata({"path":"/Good Will Hunting (1990)"})
		self.assertEqual(None, res)

	def test_startrek(self): #tv show
		res = self.parser.get_metadata({"path":"/Star Trek: The Next Generation","type":"tv series"})
		self.assertNotEqual(None, res)
		self.assertEqual(1987, res['year'])
