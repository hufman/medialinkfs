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
			"scan_mode": "files",
			"source_dir": os.path.join(self.tmpdir, "All"),
			"cache_dir": os.path.join(self.tmpdir, ".cache"),
			"output": [{
				"dest": os.path.join(self.tmpdir, "Actors"),
				"group_by": "actors"
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
		self.settings['scan_mode'] = 'directories'
		medialinkfs.organize.OrganizeSet({}, self.settings).process_all()
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "Actors", "Sir George", "testdir")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George", "testdir")))
		self.assertFalse(os.path.exists(os.path.join(self.tmpdir, "Actors", "Sir George", "testfile")))
		self.assertFalse(os.path.isfile(os.path.join(self.tmpdir, "Actors", "Sir George", "testfile")))

	def test_files(self):
		self.settings['scan_mode'] = 'files'
		medialinkfs.organize.OrganizeSet({}, self.settings).process_all()
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertFalse(os.path.exists(os.path.join(self.tmpdir, "Actors", "Sir George", "testdir")))
		self.assertFalse(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George", "testdir")))
		self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "Actors", "Sir George", "testfile")))
		self.assertTrue(os.path.isfile(os.path.join(self.tmpdir, "Actors", "Sir George", "testfile")))

	def test_toplevel(self):
		self.settings['scan_mode'] = 'toplevel'
		medialinkfs.organize.OrganizeSet({}, self.settings).process_all()
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "Actors", "Sir George", "testdir")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George", "testdir")))
		self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "Actors", "Sir George", "testfile")))
		self.assertTrue(os.path.isfile(os.path.join(self.tmpdir, "Actors", "Sir George", "testfile")))

