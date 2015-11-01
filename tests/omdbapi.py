# -*- coding: UTF-8 -*-
import os
import tempfile
import shutil
import unittest

import logging
logging.basicConfig(level=logging.DEBUG, filename='tests.log')

import medialinkfs.parsers.omdbapi as omdbapi
import tests._utils as _utils

base = os.path.dirname(__file__)

class TestOMDBAPI(_utils.TestAPI):
	def setUp(self):
		super().setUp()
		logging.debug("Initializing unittest %s"%(self.id(),))
		self.parser = omdbapi.Module({})

	def test_dynomutt(self):
		res = self.parser.get_metadata({"path":"/Dynomutt Dog Wonder"})
		self.assertNotEqual(None, res)
		res['actors'] = sorted(res['actors'])
		res['genres'] = sorted(res['genres'])
		self.assertTrue(len(res['actors']) > 1)
		self.assertEqual(1, len(res['directors']))
		self.assertEqual(2, len(res['genres']))
		self.assertTrue('Frank Welker' in res['actors'])
		self.assertTrue('Gary Owens' in res['actors'])
		self.assertTrue('Joe Ruby' in res['writers'])
		self.assertTrue('Animation' in res['genres'])

	def test_startrek(self):
		res = self.parser.get_metadata({"path":"/Star Trek (1966)"})
		self.assertNotEqual(None, res)
		self.assertEqual(1966, res['year'])

	def test_dynomutt_list(self):
		res = self.parser.search_metadata({"path":"/Dynomutt Dog Wonder"})
		self.assertNotEqual(None, res)
		self.assertEqual(2, len(res))
		self.assertEqual(0, len(res[1]))
		result = res[0]
		actors = sorted(result['actors'])
		genres = sorted(result['genres'])
		self.assertTrue(len(result['actors']) > 1)
		self.assertEqual(1, len(result['directors']))
		self.assertEqual(2, len(genres))
		self.assertTrue('Frank Welker' in actors)
		self.assertTrue('Gary Owens' in actors)
		self.assertTrue('Joe Ruby' in result['writers'])
		self.assertTrue('Animation' in genres)

	def test_startrek(self):
		res = self.parser.search_metadata({"path":"/Star Trek (1966)"})
		self.assertNotEqual(None, res)
		self.assertEqual(2, len(res))
		self.assertEqual(0, len(res[1]))
		result = res[0]
		self.assertEqual(1966, result['year'])
