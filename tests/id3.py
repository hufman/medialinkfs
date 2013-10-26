# -*- coding: UTF-8 -*-
import os
import tempfile
import shutil
import unittest

import logging
logging.basicConfig(level=logging.DEBUG, filename='tests.log')

import medialinkfs.parsers.id3 as id3

base = os.path.dirname(__file__)

class TestID3(unittest.TestCase):
	def setUp(self):
		logging.debug("Initializing unittest %s"%(self.id(),))
		self.tmpdir = tempfile.mkdtemp()
	def tearDown(self):
		shutil.rmtree(self.tmpdir)

	def test_id3(self):
		os.mkdir(os.path.join(self.tmpdir, 'All'))
		src = os.path.join(base, 'testfiles_id3', '23.synthetic.empty-extended-header.lossy.id3')
		dst = os.path.join(self.tmpdir, 'All', '23.mp3')
		shutil.copyfile(src, dst)
		res = id3.get_metadata({"path":dst})

		self.assertNotEqual(None, res)
		self.assertEqual(1, len(res['artists']))
		self.assertFalse('composers' in res)
		self.assertEqual('Combustible Edison', res['artist'])
		self.assertEqual('Combustible Edison', res['artists'][0])
		self.assertEqual('The Millionaire\'s Holiday', res['title'])

	def test_id3_folder(self):
		os.mkdir(os.path.join(self.tmpdir, 'All'))
		os.mkdir(os.path.join(self.tmpdir, 'All', 'nest'))
		src = os.path.join(base, 'testfiles_id3', '23.synthetic.empty-extended-header.lossy.id3')
		dst = os.path.join(self.tmpdir, 'All', 'nest', '23.mp3')
		shutil.copyfile(src, dst)
		src = os.path.join(base, 'testfiles_id3', '23.stagger.IPLS-frame.id3')
		dst = os.path.join(self.tmpdir, 'All', 'nest', 'test.mp3')
		shutil.copyfile(src, dst)

		res = id3.get_metadata({"path":os.path.join(self.tmpdir, 'All', 'nest')})
		self.assertNotEqual(None, res)
		self.assertEqual(2, len(res['artists']))
		self.assertFalse('composers' in res)
		self.assertEqual('Combustible Edison', sorted(res['artists'])[1])
		self.assertEqual('Album', sorted(res['albums'])[0])
