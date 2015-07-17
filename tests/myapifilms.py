# -*- coding: UTF-8 -*-
import os
import tempfile
import shutil
import unittest

import logging
logging.basicConfig(level=logging.DEBUG, filename='tests.log')

import medialinkfs.parsers.myapifilms as myapifilms

base = os.path.dirname(__file__)

class Testmyapifilms(unittest.TestCase):
	def setUp(self):
		logging.debug("Initializing unittest %s"%(self.id(),))

	def test_goodwillhunting(self):
		res = myapifilms.get_metadata({"path":"/Good Will Hunting (1997)"})
		self.assertNotEqual(None, res)
		self.assertEqual(1997, res['year'])
		self.assertEqual(8.3, res['rating'])

	def test_goodwillhunting_wrongyear_doesnotexist(self):
		res = myapifilms.get_metadata({"path":"/Good Will Hunting (1990)"})
		self.assertEqual(None, res)

	def test_startrek(self): #tv show
		res = myapifilms.get_metadata({"path":"/Star Trek: The Next Generation","type":"tv series"})
		self.assertNotEqual(None, res)
		self.assertEqual(1987, res['year'])