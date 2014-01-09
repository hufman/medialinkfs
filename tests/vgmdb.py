# -*- coding: UTF-8 -*-
import os
import tempfile
import shutil
import unittest

import logging
logging.basicConfig(level=logging.DEBUG, filename='tests.log')

import medialinkfs.parsers.vgmdb as vgmdb

base = os.path.dirname(__file__)

class TestVGMDB(unittest.TestCase):
	def setUp(self):
		logging.debug("Initializing unittest %s"%(self.id(),))

	def test_album(self):
		res = vgmdb.get_metadata({"path":"/Yuzo Koshiro Arrange Collection"})
		self.assertNotEqual(None, res)
		self.assertEqual(1, len(res['artists']))
		self.assertEqual(1, len(res['composers']))
		self.assertEqual(1, len(res['performers']))
		self.assertEqual('Yuzo Koshiro', res['artist'])
		self.assertEqual('Yuzo Koshiro', res['artists'][0])
		self.assertEqual('Yuzo Koshiro', res['composers'][0])
		self.assertEqual('Yuji Takase', res['performers'][0])
		self.assertTrue('AN' in res['arrangers'])
		self.assertTrue('Bosconian' in res['games'])

	def test_album_series(self):
		res = vgmdb.get_metadata({"path":"/Gyakuten Saiban 4 Original Soundtrack"})
		self.assertNotEqual(None, res)
		self.assertEqual(4, len(res['artists']))
		self.assertEqual(4, len(res['composers']))
		self.assertEqual('Toshihiko Horiyama', res['artist'])
		self.assertEqual('Toshihiko Horiyama', res['artists'][0])
		self.assertEqual('Akemi Kimura', res['artists'][3])
		self.assertEqual('Toshihiko Horiyama', res['composers'][0])
		self.assertEqual('Akemi Kimura', res['composers'][3])
		self.assertEqual(1, len(res['franchises']))
		self.assertEqual('Ace Attorney', res['franchise'])
		self.assertEqual('Ace Attorney', res['franchises'][0])
