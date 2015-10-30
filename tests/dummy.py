# -*- coding: UTF-8 -*-
import os
import tempfile
import shutil
import unittest

import logging
logging.basicConfig(level=logging.DEBUG, filename='tests.log')

import tests._utils as _utils
import medialinkfs
import medialinkfs.config
import medialinkfs.organize
import medialinkfs.parsers.dummy as dummy

base = os.path.dirname(__file__)

class TestDummy(_utils.TestAPI):
	def setUp(self):
		super().setUp()
		logging.debug("Initializing unittest %s"%(self.id(),))
		self.dummy_data = {"test": {
		  "actors": ["Sir George"]
		}}
		self.dummy_data_2 = {"Dynomutt Dog Wonder": {
		  "actors": ["Frank Welker"]
		}}
		self.tmpdir = tempfile.mkdtemp()
		self.secret_settings = {
			"name": "test",
			"parsers": ["dummy"],
			"parser_options": {
			  "dummy": {
			    "data": self.dummy_data
			  },
			  "dummy.2": {
			    "data": self.dummy_data_2
			  }
			},
			"scanMode": "directories",
			"sourceDir": os.path.join(self.tmpdir, "All"),
			"cacheDir": os.path.join(self.tmpdir, ".cache"),
			"output": [{
				"dest": os.path.join(self.tmpdir, "Actors"),
				"groupBy": "actors"
			}]
		}
		self.settings = medialinkfs.config.ConfigSet(self.secret_settings)
		os.mkdir(os.path.join(self.tmpdir, "All"))
		os.mkdir(os.path.join(self.tmpdir, "All", 'test'))
		os.mkdir(os.path.join(self.tmpdir, "Actors"))

	def tearDown(self):
		shutil.rmtree(self.tmpdir)

	def test_dummy(self):
		parser = dummy.Module({"data": self.dummy_data})
		res = parser.get_metadata({"path":"/test"})
		self.assertNotEqual(None, res)
		self.assertEqual(1, len(res['actors']))
		self.assertEqual("Sir George", res['actors'][0])

	def test_dummy_bad_results(self):
		# missing groupby key
		del self.dummy_data['test']['actors']
		medialinkfs.organize.organize_set({}, self.settings)

		# empty result, logs a message saying that it can't find it
		del self.dummy_data['test']
		medialinkfs.organize.organize_set({}, self.settings)

	def test_dummy_organize(self):
		# does it create the link
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))
		self.assertFalse(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test2")))
		self.assertEqual(os.readlink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")),
		                 os.path.join("..", "..", "All", "test"))

		# does it rename the link if the data changes
		os.rmdir(os.path.join(self.tmpdir, "All", 'test'))
		os.mkdir(os.path.join(self.tmpdir, "All", 'test2'))
		self.dummy_data['test2'] = self.dummy_data['test']
		del(self.dummy_data['test'])
		shutil.rmtree(self.settings['cacheDir'])
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertFalse(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test2")))
		self.assertEqual(os.readlink(os.path.join(self.tmpdir, "Actors", "Sir George", "test2")),
		                 os.path.join("..", "..", "All", "test2"))

		# does it change the link if the metadata changes
		self.dummy_data['test2']['actors'][0] = 'Sir Phil'
		shutil.rmtree(self.settings['cacheDir'])
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertFalse(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir Phil")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir Phil", "test2")))
		self.assertEqual(os.readlink(os.path.join(self.tmpdir, "Actors", "Sir Phil", "test2")),
		                 os.path.join("..", "..", "All", "test2"))

		# the actor changed from Phil to Lexus
		# does it properly clean up the old toc files from Phil's directory
		self.dummy_data['test2']['actors'][0] = 'Sir Lexus'
		lexus = os.path.join(self.tmpdir, "Actors", "Sir Lexus")
		phil = os.path.join(self.tmpdir, "Actors", "Sir Phil")
		open(os.path.join(phil, ".toc"),'w').close()
		open(os.path.join(phil, ".toc-TV"),'w').close()
		open(os.path.join(phil, ".toc.old-TV"),'w').close()
		medialinkfs.organize.fetch_set({}, self.settings)
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isdir(os.path.join(lexus)))
		self.assertFalse(os.path.islink(os.path.join(phil, "test2")))
		self.assertFalse(os.path.isfile(os.path.join(phil, ".toc")))
		self.assertFalse(os.path.isfile(os.path.join(phil, ".toc-TV")))
		self.assertFalse(os.path.isfile(os.path.join(phil, ".toc.old-TV")))
		self.assertFalse(os.path.isdir(os.path.join(phil)))

	def test_dummy_cache(self):
		# use module-level data to keep the parser_options the same
		dummy.data = dict(self.dummy_data)
		self.dummy_data.clear()
		# does it create the link
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))

		# delete the actors field and verify that it uses cache
		del dummy.data['test']['actors']
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))

		# change the data and verify that it uses the cache
		dummy.data['test']['actors'] = ['Sir Phil']
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))
		self.assertFalse(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir Phil")))
		self.assertFalse(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir Phil", "test")))

		# now clear the cache and make sure it updates
		shutil.rmtree(self.settings['cacheDir'])
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertFalse(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir Phil")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir Phil", "test")))

	def test_dummy_nocachedir(self):
		# does it create the link
		self.assertFalse(os.path.isdir(os.path.join(self.tmpdir, "All", ".cache")))
		del self.secret_settings['cacheDir']
		self.settings = medialinkfs.config.ConfigSet(self.secret_settings)
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "All", ".cache")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))

	def test_dummy_noclean(self):
		# does it create the link
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))

		# Add the setting, leaving it false
		self.secret_settings['fakeclean'] = False
		self.settings = medialinkfs.config.ConfigSet(self.secret_settings)
		self.dummy_data['test']['actors'] = ['Sir Phil']
		shutil.rmtree(self.settings['cacheDir'])
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertFalse(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))
		self.assertFalse(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir Phil")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir Phil", "test")))

		# Set the setting to true
		self.secret_settings['fakeclean'] = True
		self.settings = medialinkfs.config.ConfigSet(self.secret_settings)
		self.dummy_data['test']['actors'] = []
		shutil.rmtree(self.settings['cacheDir'])
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertFalse(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))
		self.assertFalse(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir Phil")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir Phil", "test")))

		# set the quiet noclean setting, but to false
		del self.secret_settings['fakeclean']
		self.secret_settings['noclean'] = False
		self.settings = medialinkfs.config.ConfigSet(self.secret_settings)
		self.dummy_data['test']['actors'] = ['Sir Harry']
		shutil.rmtree(self.settings['cacheDir'])
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertFalse(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir Phil", "test")))
		self.assertFalse(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir Phil")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir Harry")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir Harry", "test")))

		# set the quiet noclean setting to true
		self.secret_settings['noclean'] = True
		self.settings = medialinkfs.config.ConfigSet(self.secret_settings)
		self.dummy_data['test']['actors'] = []
		shutil.rmtree(self.settings['cacheDir'])
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertFalse(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir Phil", "test")))
		self.assertFalse(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir Phil")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir Harry")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir Harry", "test")))

	def test_dummy_deepmerge(self):
		# does it create the link
		os.rmdir(os.path.join(self.settings['sourceDir'], 'test'))
		os.mkdir(os.path.join(self.settings['sourceDir'], 'Dynomutt Dog Wonder'))
		self.dummy_data['Dynomutt Dog Wonder'] = {}
		self.dummy_data['Dynomutt Dog Wonder']['actors'] = ['Sir George']
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "Dynomutt Dog Wonder")))

		# Now, change the dummy data from Sir George to Sir Phil
		# Then, add in another parser
		# It should flush the cached data about Sir George because the new parser data
		# However, it should merge the two actors sections
		self.dummy_data['Dynomutt Dog Wonder']['actors'][0] = 'Sir Phil'
		self.secret_settings['parsers'].append('dummy.2')
		self.settings = medialinkfs.config.ConfigSet(self.secret_settings)
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertFalse(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir Phil")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Frank Welker")))

		# Try it the other way
		shutil.rmtree(self.settings['cacheDir'])
		self.secret_settings['parsers'] = ['dummy.2', 'dummy']
		self.settings = medialinkfs.config.ConfigSet(self.secret_settings)
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertFalse(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir Phil")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Frank Welker")))

	def test_dummy_dontdelete_extra(self):
		# does it create the link
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))

		# create the extra bits
		george = os.path.join(self.tmpdir, 'Actors', 'Sir George')
		os.symlink(os.path.join(self.settings['sourceDir'], 'test'),\
		        os.path.join(george, 'test.extra'))
		with open(os.path.join(george, '.toc.extra'), 'w') as extra:
			extra.write("test.extra\n")

		# run the organization again, make sure it didn't delete our extra
		shutil.rmtree(self.settings['cacheDir'])
		self.dummy_data['test']['actors'][0] = 'Sir Phil'
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isfile(os.path.join(george, '.toc.extra')))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertFalse(os.path.islink(os.path.join(george, 'test')))
		self.assertTrue(os.path.islink(os.path.join(george, 'test.extra')))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir Phil")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir Phil", 'test')))

		# run it again, make sure that the extra file wasn't deleted
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isfile(os.path.join(george, '.toc.extra')))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertFalse(os.path.islink(os.path.join(george, 'test')))
		self.assertTrue(os.path.islink(os.path.join(george, 'test.extra')))
	def test_dummy_dontdelete_file(self):
		# does it create the link
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))

		# make a real file
		with open(os.path.join(self.tmpdir, "Actors", "Sir George", "file"), 'w') as output:
			output.write("test file\n")

		# run the organization again, make sure it doesn't delete our file
		shutil.rmtree(self.settings['cacheDir'])
		self.dummy_data['test']['actors'][0] = 'Sir Phil'
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertFalse(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", 'test')))
		self.assertTrue(os.path.isfile(os.path.join(self.tmpdir, "Actors", "Sir George", 'file')))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir Phil")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir Phil", 'test')))

	def test_dummy_multiset(self):
		# does it create the link
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))

		newtmp = tempfile.mkdtemp()
		try:
			secret_settings = {
				"name": "test2",
				"parsers": ["dummy"],
				"parser_options": {"dummy": {
					"data": self.dummy_data
				}},
				"scanMode": "directories",
				"sourceDir": os.path.join(newtmp),
				"cacheDir": os.path.join(newtmp, ".cache"),
				"output": [{
					"dest": os.path.join(self.tmpdir, "Actors"),
					"groupBy": "actors"
				}]
			}
			os.mkdir(os.path.join(newtmp, 'test2'))
			settings = medialinkfs.config.ConfigSet(secret_settings)
			self.dummy_data['test2'] = {'actors':['Sir George']}

			# try it
			medialinkfs.organize.organize_set({}, settings)
			self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
			self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))
			self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test2")))

			# try it with the old .toc.done file
			os.rename(os.path.join(self.tmpdir, "Actors", "Sir George", ".toc.done-test"), \
			          os.path.join(self.tmpdir, "Actors", "Sir George", ".toc.done"))
			shutil.rmtree(settings['cacheDir'])
			medialinkfs.organize.organize_set({}, settings)
			self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
			self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))
			self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test2")))

		finally:
			shutil.rmtree(newtmp)

	def test_dummy_parser_options(self):
		# does it create the link
		self.secret_settings['parser_options'] = {
		  'dummy': {'data': {
		    'test': {
		      'should_exist':'True'
		    }
		  }},
		  'fake': {'data': {
		    'test': {
		      'should_exist':'False'
		    }
		  }}
		}
		self.secret_settings['output'][0]['groupBy'] = 'should_exist'
		self.settings = medialinkfs.config.ConfigSet(self.secret_settings)
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertFalse(os.path.isdir(os.path.join(self.tmpdir, "Actors", "False")))
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "True")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "True", "test")))

	def test_dummy_regex(self):
		self.secret_settings['regex'] = '^.*tst$'
		self.settings = medialinkfs.config.ConfigSet(self.secret_settings)
		self.dummy_data['test.tst'] = self.dummy_data['test']
		os.mkdir(os.path.join(self.tmpdir, 'All', 'test.tst'))
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertFalse(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test.tst")))

	def test_dummy_multiple_groups(self):
		self.secret_settings['output'][0]['groupBy'] = ['actors', 'extras']
		self.settings = medialinkfs.config.ConfigSet(self.secret_settings)
		self.dummy_data['test2'] = {"extras": ["Sir George"]}
		os.mkdir(os.path.join(self.tmpdir, 'All', 'test2'))
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test2")))
	def test_dummy_multiple_identical_groups(self):
		self.secret_settings['output'][0]['groupBy'] = ['actors', 'extras']
		self.settings = medialinkfs.config.ConfigSet(self.secret_settings)
		self.dummy_data['test'] = {"actors": ["Sir George"], "extras": ["Sir George"]}
		os.mkdir(os.path.join(self.tmpdir, 'All', 'test2'))
		medialinkfs.organize.organize_set({}, self.settings)
		self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, "Actors", "Sir George")))
		self.assertTrue(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test")))
		self.assertFalse(os.path.islink(os.path.join(self.tmpdir, "Actors", "Sir George", "test2")))
