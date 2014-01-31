# -*- coding: UTF-8 -*-
import os
import tempfile
import shutil
import unittest

import logging
logging.basicConfig(level=logging.DEBUG, filename='tests.log')

import medialinkfs.parsers.parsename as parsename

base = os.path.dirname(__file__)

class TestName(unittest.TestCase):
	def setUp(self):
		logging.debug("Initializing unittest %s"%(self.id(),))

	def test_year(self):
		res = parsename.get_metadata({"path":"/Schfifty Five"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertFalse('year' in res)

		res = parsename.get_metadata({"path":"/Schfifty Five (1955)"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertTrue('year' in res)
		self.assertEqual(1955, res['year'])

		res = parsename.get_metadata({"path":"/Schfifty Five [1955]"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertTrue('year' in res)
		self.assertEqual(1955, res['year'])

	def test_res(self):
		res = parsename.get_metadata({"path":"/Schfifty Five"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertFalse('year' in res)

		res = parsename.get_metadata({"path":"/Schfifty Five (720)"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertTrue('resolution' in res)
		self.assertEqual(720, res['resolution'])
		self.assertFalse('interlaced' in res)

		res = parsename.get_metadata({"path":"/Schfifty Five (720p)"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertTrue('resolution' in res)
		self.assertEqual(720, res['resolution'])
		self.assertFalse('interlaced' in res)

		res = parsename.get_metadata({"path":"/Schfifty Five (720i)"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertTrue('resolution' in res)
		self.assertEqual(720, res['resolution'])
		self.assertTrue('interlaced' in res)
		self.assertTrue(res['interlaced'])

	def test_dots(self):
		res = parsename.get_metadata({"path":"/Schfifty.Five"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertFalse('year' in res)

		res = parsename.get_metadata({"path":"/Schfifty.Five.(720p)"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertTrue('resolution' in res)
		self.assertEqual(720, res['resolution'])
		self.assertFalse('interlaced' in res)

	def test_scene(self):
		res = parsename.get_metadata({"path":"/Schfifty Five"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertFalse('year' in res)

		res = parsename.get_metadata({"path":"/Schfifty Five (x264-Scene)"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertTrue('format' in res)
		self.assertEqual('x264', res['format'])
		self.assertTrue('release_group' in res)
		self.assertEqual('Scene', res['release_group'])

		res = parsename.get_metadata({"path":"/Schfifty Five (avc_Scene)"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertTrue('format' in res)
		self.assertEqual('avc', res['format'])
		self.assertTrue('release_group' in res)
		self.assertEqual('Scene', res['release_group'])

		res = parsename.get_metadata({"path":"/Schfifty.Five.avc_Scene"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertTrue('format' in res)
		self.assertEqual('avc', res['format'])
		self.assertTrue('release_group' in res)
		self.assertEqual('Scene', res['release_group'])

	def test_format(self):
		res = parsename.get_metadata({"path":"/Schfifty.Five"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertFalse('year' in res)

		res = parsename.get_metadata({"path":"/Schfifty Five (x264)"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertTrue('format' in res)
		self.assertEqual('x264', res['format'])

		res = parsename.get_metadata({"path":"/Schfifty Five (X264)"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertTrue('format' in res)
		self.assertEqual('x264', res['format'])

		res = parsename.get_metadata({"path":"/Schfifty Five (H264)"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertTrue('format' in res)
		self.assertEqual('h264', res['format'])

		res = parsename.get_metadata({"path":"/Schfifty Five (AVC)"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertTrue('format' in res)
		self.assertEqual('avc', res['format'])

	def test_filename(self):
		res = parsename.get_metadata({"path":"/Schfifty.Five.(1955).720p"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertTrue('year' in res)
		self.assertEqual(1955, res['year'])
		self.assertTrue('resolution' in res)
		self.assertEqual(720, res['resolution'])
		self.assertFalse('interlaced' in res)
		self.assertFalse('extension' in res)

		res = parsename.get_metadata({"path":"/Schfifty.Five.(1955).720p.mkv"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertTrue('year' in res)
		self.assertEqual(1955, res['year'])
		self.assertTrue('resolution' in res)
		self.assertEqual(720, res['resolution'])
		self.assertFalse('interlaced' in res)
		self.assertTrue('extension' in res)
		self.assertEqual('mkv', res['extension'])

		res = parsename.get_metadata({"path":"/Schfifty.Five.(1955).720p.jpg"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertTrue('year' in res)
		self.assertEqual(1955, res['year'])
		self.assertTrue('resolution' in res)
		self.assertEqual(720, res['resolution'])
		self.assertFalse('interlaced' in res)
		self.assertTrue('extension' in res)
		self.assertEqual('jpg', res['extension'])

	def test_combined(self):
		res = parsename.get_metadata({"path":"/Schfifty.Five.(1955).720p"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertTrue('year' in res)
		self.assertEqual(1955, res['year'])
		self.assertTrue('resolution' in res)
		self.assertEqual(720, res['resolution'])
		self.assertFalse('interlaced' in res)

		res = parsename.get_metadata({"path":"/Schfifty.Five.(1955)[720i]"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertTrue('year' in res)
		self.assertEqual(1955, res['year'])
		self.assertTrue('resolution' in res)
		self.assertEqual(720, res['resolution'])
		self.assertTrue('interlaced' in res)
		self.assertTrue(res['interlaced'])

		res = parsename.get_metadata({"path":"/Schfifty.Five(1955)[720i].avi"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertTrue('year' in res)
		self.assertEqual(1955, res['year'])
		self.assertTrue('resolution' in res)
		self.assertEqual(720, res['resolution'])
		self.assertTrue('interlaced' in res)
		self.assertTrue(res['interlaced'])
		self.assertTrue('extension' in res)
		self.assertEqual('avi', res['extension'])

		res = parsename.get_metadata({"path":"/Schfifty.Five.1955.720p.h264-scene.mkv"})
		self.assertNotEqual(None, res)
		self.assertEqual('Schfifty Five', res['name'])
		self.assertTrue('year' in res)
		self.assertEqual(1955, res['year'])
		self.assertTrue('resolution' in res)
		self.assertEqual(720, res['resolution'])
		self.assertFalse('interlaced' in res)
		self.assertTrue('format' in res)
		self.assertEqual('h264', res['format'])
		self.assertTrue('release_group' in res)
		self.assertEqual('scene', res['release_group'])
		self.assertTrue('extension' in res)
		self.assertEqual('mkv', res['extension'])
