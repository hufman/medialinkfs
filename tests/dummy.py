# -*- coding: UTF-8 -*-
import os
import tempfile
import shutil
import unittest

import logging
#logging.basicConfig(level=logging.DEBUG)

import medialinkfs
import medialinkfs.organize
import medialinkfs.parsers.dummy as dummy

base = os.path.dirname(__file__)

class TestDummy(unittest.TestCase):
	def setUp(self):
		dummy.data = {"test": {
		  "actors": ["Sir George"]
		}}
		self.tmpdir = tempfile.mkdtemp()
		self.settings = {
			"name": "test",
			"parsers": ["dummy"],
			"scanMode": "directories",
			"sourceDir": os.path.join(self.tmpdir, "All"),
			"cacheDir": os.path.join(self.tmpdir, ".cache"),
			"output": [{
				"dest": os.path.join(self.tmpdir, "Actors"),
				"groupBy": "actors"
			}]
		}
		os.mkdir(os.path.join(self.tmpdir, "All"))
		os.mkdir(os.path.join(self.tmpdir, "All", 'test'))
		os.mkdir(os.path.join(self.tmpdir, "Actors"))

	def tearDown(self):
		shutil.rmtree(self.tmpdir)

	def test_dummy(self):
		res = dummy.get_metadata("/test")
		self.assertNotEqual(None, res)
		self.assertEqual(1, len(res['actors']))
		self.assertEqual("Sir George", res['actors'][0])

	def test_dummy_bad_results(self):
		# missing groupby key
		del dummy.data['test']['actors']
		medialinkfs.organize.organize_set({}, self.settings)

		# empty result
		del dummy.data['test']
		medialinkfs.organize.organize_set({}, self.settings)

	def test_dummy_organize(self):
		# does it create the link
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))
		self.assertFalse(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test2")))

		# does it rename the link if the data changes
		os.rmdir(os.path.join(self.tmpdir, "All", 'test'))
		os.mkdir(os.path.join(self.tmpdir, "All", 'test2'))
		dummy.data['test2'] = dummy.data['test']
		del(dummy.data['test'])
		shutil.rmtree(self.settings['cacheDir'])
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertFalse(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test2")))

		# does it change the link if the metadata changes
		dummy.data['test2']['actors'][0] = 'Sir Phil'
		shutil.rmtree(self.settings['cacheDir'])
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertFalse(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir Phil")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir Phil", "test2")))

	def test_dummy_cache(self):
		# does it create the link
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))

		# delete the actors field and see if it uses cache
		del dummy.data['test']['actors']
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))

		# now prefer the cache, even if the data has changed
		dummy.data['test']['actors'] = ['Sir Phil']
		self.settings['preferCachedData'] = True
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))
		self.assertFalse(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir Phil")))
		self.assertFalse(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir Phil", "test")))

		# now clear the cache and make sure it updates
		shutil.rmtree(self.settings['cacheDir'])
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertFalse(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir Phil")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir Phil", "test")))

	def test_dummy_noclean(self):
		# does it create the link
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))

		# Add the setting, leaving it false
		self.settings['fakeclean'] = False
		dummy.data['test']['actors'] = ['Sir Phil']
		shutil.rmtree(self.settings['cacheDir'])
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertFalse(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))
		self.assertFalse(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir Phil")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir Phil", "test")))

		# Set the setting to true
		self.settings['fakeclean'] = True
		dummy.data['test']['actors'] = []
		shutil.rmtree(self.settings['cacheDir'])
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertFalse(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))
		self.assertFalse(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir Phil")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir Phil", "test")))

		# set the quiet noclean setting, but to false
		del self.settings['fakeclean']
		self.settings['noclean'] = False
		dummy.data['test']['actors'] = ['Sir Harry']
		shutil.rmtree(self.settings['cacheDir'])
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertFalse(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir Phil", "test")))
		self.assertFalse(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir Phil")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir Harry")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir Harry", "test")))

		# set the quiet noclean setting to true
		self.settings['noclean'] = True
		dummy.data['test']['actors'] = []
		shutil.rmtree(self.settings['cacheDir'])
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertFalse(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir Phil", "test")))
		self.assertFalse(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir Phil")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir Harry")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir Harry", "test")))
