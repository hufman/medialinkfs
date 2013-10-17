# -*- coding: UTF-8 -*-
import os
import tempfile
import shutil
import unittest

import logging
logging.basicConfig(level=logging.DEBUG, filename='tests.log')

import medialinkfs.parsers.mymovieapi as mymovieapi

base = os.path.dirname(__file__)

class TestMYMOVIEAPI(unittest.TestCase):
	def setUp(self):
		logging.debug("Initializing unittest %s"%(self.id(),))

	def test_dynomutt(self):
		res = mymovieapi.get_metadata("/Dynomutt Dog Wonder")
		self.assertNotEqual(None, res)
		res['actors'] = sorted(res['actors'])
		res['genres'] = sorted(res['genres'])
		self.assertEqual(2, len(res['actors']))
		self.assertEqual(2, len(res['genres']))
		self.assertEqual('Frank Welker', res['actors'][0])
		self.assertEqual('Gary Owens', res['actors'][1])
		self.assertEqual('Animation', res['genres'][0])

	def test_startrek(self):
		res = mymovieapi.get_metadata("/Star Trek (1966)")
		self.assertNotEqual(None, res)
		self.assertEqual(1966, res['year'])

	def test_startrek_tv(self):
		options = {"type": "tv series"}
		res = mymovieapi.get_metadata("/Star Trek", options)
		self.assertNotEqual(None, res)
		self.assertEqual(1966, res['year'])

	def test_startrek_movie(self):
		options = {"type": "movie"}
		res = mymovieapi.get_metadata("/Star Trek", options)
		self.assertNotEqual(None, res)
		self.assertEqual(2009, res['year'])
