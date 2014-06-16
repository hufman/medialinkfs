# -*- coding: UTF-8 -*-
import os
import tempfile
import shutil
import unittest

import logging
logging.basicConfig(level=logging.DEBUG, filename='tests.log')

import medialinkfs.parsers.freebase as api
import medialinkfs.config

base = os.path.dirname(__file__)
config_file = os.path.join(base,"..","config.yml")
settings = {}
try:
	config = medialinkfs.config.import_config(config_file)
	settings['api_key'] = self.config['global_settings']['parser_options']['freebase']['api_key']
except:
	logging.warning("Could not load API key from config file %s, lack of API key may cause test failures"%(config_file,))
	pass

class TestFreebase(unittest.TestCase):
	def setUp(self):
		logging.debug("Initializing unittest %s"%(self.id(),))
		self.config = {}
		self.settings = dict(settings)

	def test_dynomutt(self):
		self.settings['type'] = '/tv/tv_program'
		res = api.get_metadata({"path":"/Dynomutt Dog Wonder"}, self.settings)
		self.assertNotEqual(None, res)
		res['actors'] = sorted(res['actors'])
		res['genres'] = sorted(res['genres'])
		self.assertEqual(4, len(res['actors']))
		self.assertEqual(3, len(res['producers']))
		self.assertEqual(3, len(res['genres']))
		self.assertEqual(0, len(res['aka']))
		self.assertEqual(0, len(res['writers']))
		self.assertEqual('Frank Welker', res['actors'][0])
		self.assertEqual('Gary Owens', res['actors'][1])
		self.assertEqual('Joseph Barbera', res['producers'][0])
		self.assertEqual('Animation', res['genres'][0])
		self.assertEqual('English Language', res['languages'][0])
		self.assertEqual('United States of America', res['countries'][0])
		self.assertEqual('American Broadcasting Company', res['network'][0])

	def test_startrek_tv(self):
		self.settings['type'] = '/tv/tv_program'
		res = api.get_metadata({"path":"/Star Trek TOS"}, self.settings)
		self.assertNotEqual(None, res)
		self.assertEqual('1966-09-08', res['release_date'])
		self.assertEqual(2, len(res['aka']))
		self.assertEqual(1, len(res['writers']))
		self.assertEqual(9, len(res['producers']))
		self.assertEqual(5, len(res['genres']))
		self.assertEqual(11, len(res['actors']))
		self.assertEqual('NBC', res['network'])
		self.assertEqual('United States of America', res['countries'][0])
		self.assertEqual('English Language', res['languages'][0])
		self.assertEqual('Gene Roddenberry', res['writers'][0])
		self.assertEqual('Gene Roddenberry', res['producers'][0])
		self.assertEqual('Science Fiction', res['genres'][0])
		self.assertEqual('William Shatner', res['actors'][0])

	def test_startrek_tv(self):
		self.settings['type'] = '/tv/tv_program'
		res = api.get_metadata({"path":"/Star Trek (1966)"}, self.settings)
		self.assertNotEqual(None, res)
		self.assertEqual('1966-09-08', res['release_date'])

	def test_leagues(self):
		self.settings['type'] = '/film/film'
		res = api.get_metadata({"path":"/20,000 Leagues Under the Sea (1954)"}, self.settings)
		self.assertNotEqual(None, res)
		self.assertEqual('1954-12-23', res['release_date'])

	def test_startrek_movie(self):
		self.settings['type'] = '/film/film'
		res = api.get_metadata({"path":"/Star Trek"}, self.settings)
		self.assertNotEqual(None, res)
		self.assertEqual('2009-04-06', res['release_date'])
		self.assertEqual(1, len(res['composers']))
		self.assertEqual(1, len(res['directors']))
		self.assertEqual(2, len(res['producers']))
		self.assertEqual(2, len(res['editors']))
		self.assertEqual(1, len(res['series']))
		self.assertEqual(3, len(res['genres']))
		self.assertEqual(100, len(res['actors']))	# api search limit
		self.assertEqual('Star Trek', res['series'][0])
		self.assertEqual('Action', res['genres'][0])
		self.assertEqual('United States of America', res['countries'][0])
		self.assertEqual('Germany', res['countries'][1])
		self.assertEqual('English Language', res['languages'][0])
		self.assertEqual('Michael Giacchino', res['composers'][0])
		self.assertEqual('J.J. Abrams', res['directors'][0])
		self.assertEqual('J.J. Abrams', res['producers'][0])
		self.assertEqual('Mary Jo Markey', res['editors'][0])
		self.assertEqual('Alex Kurtzman', res['writers'][0])

	def test_gattaca(self):
		res = api.get_metadata({"path":"/Gattaca"}, self.settings)
		self.assertNotEqual(None, res)
		self.assertTrue('/film/film' in res['freebase_type'])
		self.assertEqual('Ethan Hawke', res['actors'][0])
		self.assertEqual('1997-09-07', res['release_date'])
		self.assertEqual('Science Fiction', res['genres'][0])
		self.assertEqual('Genetic engineering', res['subjects'][0])
		self.assertEqual('Andrew Niccol', res['writers'][0])
		self.assertEqual('Danny DeVito', res['producers'][0])

	def test_fantasia(self):
		""" Fantasia has a strange null actor """
		self.settings['type'] = '/film/film'
		res = api.get_metadata({"path":"/Fantasia"}, self.settings)
		self.assertNotEqual(None, res)
		self.assertFalse(any(map(lambda x:x == None, res['actors'])))
		self.assertEqual(7, len(res['actors']))

	def test_black_adder(self):
		""" Black Adder has a null release_date """
		self.settings['type'] = '/tv/tv_program'
		res = api.get_metadata({"path":"/Black Adder"}, self.settings)
		self.assertNotEqual(None, res)
		self.assertFalse(any(map(lambda x:x == None, res['actors'])))
		self.assertEqual(6, len(res['actors']))

	def test_manwire(self):
		""" Man On Wire is part of Law &amp; Crime genrer """
		self.settings['type'] = '/film/film'
		res = api.get_metadata({"path":"/Man On Wire"}, self.settings)
		self.assertNotEqual(None, res)
		self.assertFalse('Law &amp; Crime' in res['genres'])
		self.assertTrue('Law & Crime' in res['genres'])

	def test_custom(self):
		self.settings['type'] = '/time/calendar'
		self.settings['searches'] = [{
			'name~=':'name'
		}]
		self.settings['properties'] = {
			'/time/calendar/days_of_week': []
		}
		self.settings['renames'] = {
			'/time/calendar/days_of_week': 'days'
		}
		res = api.get_metadata({"path":"/Gregorian Calendar"}, self.settings)
		self.assertNotEqual(None, res)
		self.assertEqual(7, len(res['days']))
		self.assertEqual('Sunday', res['days'][0])
