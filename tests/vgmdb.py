# -*- coding: UTF-8 -*-
import os
import tempfile
import shutil
import unittest

import logging
logging.basicConfig(level=logging.DEBUG, filename='tests.log')

import medialinkfs.parsers.vgmdb as vgmdb
import tests._utils as _utils

base = os.path.dirname(__file__)

class TestVGMDB(_utils.TestAPI):
	def setUp(self):
		super().setUp()
		logging.debug("Initializing unittest %s"%(self.id(),))

	def test_album(self):
		res = vgmdb.get_metadata({"path":"/Suteki Da Ne featured in Final Fantasy X"})
		self.assertNotEqual(None, res)
		self.assertEqual(2, len(res['artists']))
		self.assertEqual(2, len(res['composers']))
		self.assertEqual(10, len(res['performers']))
		self.assertEqual('Nobuo Uematsu', res['artist'])
		self.assertEqual('Nobuo Uematsu', res['artists'][0])
		self.assertEqual('Nobuo Uematsu', res['composers'][0])
		self.assertEqual('RIKKI', res['performers'][0])
		self.assertTrue('Shiro Hamaguchi' in res['arrangers'])
		self.assertTrue('Final Fantasy X' in res['games'])

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
