# -*- coding: UTF-8 -*-
import os
import tempfile
import shutil
import unittest

import logging
logging.basicConfig(level=logging.DEBUG, filename='tests.log')

import medialinkfs
import medialinkfs.deepmerge as deepmerge

base = os.path.dirname(__file__)

class TestUtils(unittest.TestCase):
	def setUp(self):
		logging.debug("Initializing unittest %s"%(self.id(),))

	def test_deep_merge_str(self):
		meta = {"actors":"yes"}
		new = {"people":"no"}
		deepmerge.deep_merge(meta, new)
		self.assertEqual(2, len(meta.keys()))
		self.assertEqual("yes", meta['actors'])
		self.assertEqual("no", meta['people'])

	def test_deep_merge_str_conflict(self):
		meta = {"actors":"yes"}
		new = {"actors":"no"}
		deepmerge.deep_merge(meta, new)
		self.assertEqual(1, len(meta.keys()))
		self.assertEqual("no", meta['actors'])

	def test_deep_merge_dict(self):
		meta = {"actors":True}
		new = {"things":True}
		deepmerge.deep_merge(meta, new)
		self.assertEqual(2, len(meta.keys()))
		self.assertTrue(meta['actors'])
		self.assertTrue(meta['things'])

	def test_deep_merge_nested_str(self):
		meta = {"actors":{"one":"one"}}
		new = {"actors":{"two":"two"}}
		deepmerge.deep_merge(meta, new)
		self.assertEqual(2, len(meta['actors'].keys()))
		self.assertTrue(meta['actors']['one'])
		self.assertTrue(meta['actors']['two'])

	def test_deep_merge_nested_str_conflict(self):
		meta = {"actors":{"one":"one", "two":"two"}}
		new = {"actors":{"two":"two"}}
		deepmerge.deep_merge(meta, new)
		self.assertEqual(2, len(meta['actors'].keys()))
		self.assertTrue(meta['actors']['one'])
		self.assertTrue(meta['actors']['two'])

	def test_deep_merge_nested_dict(self):
		meta = {"actors":{"one":True}}
		new = {"actors":{"two":True}}
		deepmerge.deep_merge(meta, new)
		self.assertEqual(2, len(meta['actors'].keys()))
		self.assertTrue(meta['actors']['one'])
		self.assertTrue(meta['actors']['two'])

	def test_deep_merge_nested_dict_conflict(self):
		meta = {"actors":{"one":True, "two":True}}
		new = {"actors":{"two":True}}
		deepmerge.deep_merge(meta, new)
		self.assertEqual(2, len(meta['actors'].keys()))
		self.assertTrue(meta['actors']['one'])
		self.assertTrue(meta['actors']['two'])

	def test_deep_merge_nested_list(self):
		meta = {"actors":["one","two"]}
		new = {"actors":["two","three"]}
		deepmerge.deep_merge(meta, new)
		self.assertEqual(3, len(meta['actors']))
		self.assertTrue('one' in meta['actors'])
		self.assertTrue('two' in meta['actors'])
		self.assertTrue('three' in meta['actors'])
