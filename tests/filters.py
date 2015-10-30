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
		self.quantizer = quantizer.Module({})

	def tearDown(self):
		shutil.rmtree(self.tmpdir)

	def test_decade(self):
		res = self.quantizer.get_metadata(dummy.data['test'])
		self.assertNotEqual(None, res)
		self.assertEqual('1979', res['year'])
		self.assertTrue('decade' in res)
		self.assertEqual("1970", res['decade'])
		self.assertEqual("1970s", res['decades'])

	def test_empty_decade(self):
		del dummy.data['test']['year']
		res = self.quantizer.get_metadata(dummy.data['test'])
		self.assertNotEqual(None, res)
		self.assertFalse('decade' in res)

	def test_decade_organize(self):
		medialinkfs.organize.OrganizeSet({}, self.settings).process_all()
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Year", "1979")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Decade", "1970")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Decades", "1970s")))

	def test_release_date(self):
		res = {"release_date":"2012-09-06"}
		res = self.quantizer.get_metadata(res)
		self.assertTrue('year' in res)
		self.assertEqual('2012', res['year'])
		self.assertTrue('decade' in res)
		self.assertEqual('2010', res['decade'])
		self.assertEqual('2010s', res['decades'])

	def test_release_date_organize(self):
		dummy.data['test']['release_date]'] = "1979-09-06"
		res = self.quantizer.get_metadata(dummy.data['test'])
		medialinkfs.organize.OrganizeSet({}, self.settings).process_all()
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Year", "1979")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Decade", "1970")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Decades", "1970s")))

	def test_letters(self):
		res = {"name":"This is a movie"}
		res = self.quantizer.get_metadata(res)
		self.assertEqual('T', res['letter'])

	def test_letters_special(self):
		res = {"name":"1234 This is a movie"}
		res = self.quantizer.get_metadata(res)
		self.assertEqual('0', res['letter'])

	def test_ratings(self):
		res = {"rating":"8.3"}
		res = self.quantizer.get_metadata(res)
		self.assertEqual('8.5', res['ratings'])
