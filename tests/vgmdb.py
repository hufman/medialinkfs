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
		self.parser = vgmdb.Module({})

	def test_album(self):
		res = self.parser.get_metadata({"path":"/Suteki Da Ne featured in Final Fantasy X"})
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
		self.assertEqual('2004', res['year'])

	def test_album_series(self):
		res = self.parser.get_metadata({"path":"/Gyakuten Saiban 4 Original Soundtrack"})
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

	def test_album_list(self):
		res = self.parser.search_metadata({"path":"/Suteki Da Ne featured in Final Fantasy X"})
		self.assertNotEqual(None, res)
		self.assertEqual(1, len(res[1]))	# one other result
		result = res[0]
		self.assertEqual(2, len(result['artists']))
		self.assertEqual(2, len(result['composers']))
		self.assertEqual(10, len(result['performers']))
		self.assertEqual('Nobuo Uematsu', result['artist'])
		self.assertEqual('Nobuo Uematsu', result['artists'][0])
		self.assertEqual('Nobuo Uematsu', result['composers'][0])
		self.assertEqual('RIKKI', result['performers'][0])
		self.assertTrue('Shiro Hamaguchi' in result['arrangers'])
		self.assertTrue('Final Fantasy X' in result['games'])
		self.assertEqual('2004', result['year'])
		result = res[1][0]
		self.assertEqual('2001-07-18', result['release_date'])
		self.assertEqual('SSCX-10053', result['catalog'])

	def test_album_series_list(self):
		res = self.parser.search_metadata({"path":"/Gyakuten Saiban 4 Original Soundtrack"})
		self.assertNotEqual(None, res)
		self.assertEqual(7, len(res[1]))
		result = res[0]
		self.assertEqual(4, len(result['artists']))
		self.assertEqual(4, len(result['composers']))
		self.assertEqual('Toshihiko Horiyama', result['artist'])
		self.assertEqual('Toshihiko Horiyama', result['artists'][0])
		self.assertEqual('Akemi Kimura', result['artists'][3])
		self.assertEqual('Toshihiko Horiyama', result['composers'][0])
		self.assertEqual('Akemi Kimura', result['composers'][3])
		self.assertEqual(1, len(result['franchises']))
		self.assertEqual('Ace Attorney', result['franchise'])
		self.assertEqual('Ace Attorney', result['franchises'][0])
		result = sorted(res[1], key=lambda x: x['catalog'])[0]
		self.assertEqual('Gyakuten Saiban Yomigaeru Gyakuten Original Soundtrack', result['titles']['en'])
