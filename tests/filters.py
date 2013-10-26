# -*- coding: UTF-8 -*-
import os
import tempfile
import shutil
import unittest

import logging
logging.basicConfig(level=logging.DEBUG, filename='tests.log')

import medialinkfs
import medialinkfs.organize
import medialinkfs.parsers.dummy as dummy
import medialinkfs.parsers.quantizer as quantizer

base = os.path.dirname(__file__)

class TestFilters(unittest.TestCase):
	def setUp(self):
		logging.debug("Initializing unittest %s"%(self.id(),))
		dummy.data = {"test": {
		  "year": '1979'
		}}
		self.tmpdir = tempfile.mkdtemp()
		self.settings = {
			"name": "test",
			"parsers": ["dummy","quantizer"],
			"scanMode": "directories",
			"sourceDir": os.path.join(self.tmpdir, "All"),
			"cacheDir": os.path.join(self.tmpdir, ".cache"),
			"output": [{
				"dest": os.path.join(self.tmpdir, "Year"),
				"groupBy": "year"
			},{
				"dest": os.path.join(self.tmpdir, "Decade"),
				"groupBy": "decade"
			},{
				"dest": os.path.join(self.tmpdir, "Decades"),
				"groupBy": "decades"
			}]
		}
		os.mkdir(os.path.join(self.tmpdir, "All"))
		os.mkdir(os.path.join(self.tmpdir, "All", 'test'))
		os.mkdir(os.path.join(self.tmpdir, "Year"))
		os.mkdir(os.path.join(self.tmpdir, "Decade"))
		os.mkdir(os.path.join(self.tmpdir, "Decades"))

	def tearDown(self):
		shutil.rmtree(self.tmpdir)

	def test_decade(self):
		res = quantizer.get_metadata(dummy.data['test'])
		self.assertNotEqual(None, res)
		self.assertFalse('year' in res)
		self.assertTrue('decade' in res)
		self.assertEqual("1970", res['decade'])
		self.assertEqual("1970s", res['decades'])

	def test_empty_decade(self):
		del dummy.data['test']['year']
		res = quantizer.get_metadata(dummy.data['test'])
		self.assertNotEqual(None, res)
		self.assertFalse('decade' in res)

	def test_decade_organize(self):
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Year", "1979")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Decade", "1970")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Decades", "1970s")))
