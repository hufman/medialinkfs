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

base = os.path.dirname(__file__)

class TestModes(unittest.TestCase):
	def setUp(self):
		logging.debug("Initializing unittest %s"%(self.id(),))
		dummy.data = {
		  "testfile": {
		    "actors": ["Sir George"]
		  },
		  "testdir": {
		    "actors": ["Sir George"]
		  },
		}
		self.tmpdir = tempfile.mkdtemp()
		self.settings = {
			"name": "test",
			"parsers": ["dummy"],
			"scanMode": "files",
			"sourceDir": os.path.join(self.tmpdir, "All"),
			"cacheDir": os.path.join(self.tmpdir, ".cache"),
			"output": [{
				"dest": os.path.join(self.tmpdir, "Actors"),
				"groupBy": "actors"
			}]
		}
		os.mkdir(os.path.join(self.tmpdir, "All"))
		os.mkdir(os.path.join(self.tmpdir, "All", "testdir"))
		with open(os.path.join(self.tmpdir, "All", "testfile"), 'w'):
			# empty file
			pass
		os.mkdir(os.path.join(self.tmpdir, "Actors"))

	def tearDown(self):
		shutil.rmtree(self.tmpdir)

	def test_directories(self):
		self.settings['scanMode'] = 'directories'
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "Actors", "Sir George", "testdir")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George", "testdir")))
		self.assertFalse(os.path.exists(os.path.join(self.tmpdir, "Actors", "Sir George", "testfile")))
		self.assertFalse(os.path.isfile(os.path.join(self.tmpdir, "Actors", "Sir George", "testfile")))

	def test_files(self):
		self.settings['scanMode'] = 'files'
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertFalse(os.path.exists(os.path.join(self.tmpdir, "Actors", "Sir George", "testdir")))
		self.assertFalse(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George", "testdir")))
		self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "Actors", "Sir George", "testfile")))
		self.assertTrue(os.path.isfile(os.path.join(self.tmpdir, "Actors", "Sir George", "testfile")))

	def test_toplevel(self):
		self.settings['scanMode'] = 'toplevel'
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "Actors", "Sir George", "testdir")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George", "testdir")))
		self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "Actors", "Sir George", "testfile")))
		self.assertTrue(os.path.isfile(os.path.join(self.tmpdir, "Actors", "Sir George", "testfile")))

