import os.path
import httpretty
import urllib.request
import unittest
import re

import logging
logging.basicConfig(level=logging.DEBUG, filename='tests.log')

tests_dir = os.path.dirname(__file__)

class TestAPI(unittest.TestCase):
	""" A Unit Test that tries to hit an API
	Will save a copy of the response to a local directory
	and use that to mock responses to that API
	"""
	def setUp(self):
		logging.debug("Starting up TestAPI mock")
		self._mock_enable()

	def _mock_enable(self):
		httpretty.enable()
		httpretty.register_uri(httpretty.GET, re.compile('.*'), body=self._mock_api)

	def _cache_dir(self, method, uri, headers):
		return os.path.join(tests_dir, 'mock_api')
	def _cache_filename(self, method, uri, headers):
		return uri.replace('/', '／')
	def _cache_path(self, method, uri, headers):
		return os.path.join(self._cache_dir(method, uri, headers),
		                    self._cache_filename(method, uri, headers))

	def _mock_api(self, method, uri, headers):
		path = self._cache_path(method, uri, headers)
		logging.debug("Looking for cached API response for %s at %s" % (uri, path))
		if not os.path.exists(path):
			logging.debug("Fetching API response from %s" % (uri,))
			self._mock_disable()
			request = urllib.request.Request(uri, headers=headers)
			with urllib.request.urlopen(request) as response:
				with open(path, 'wb') as output:
					data = response.read()
					output.write(data)
			self._mock_enable()
		with open(path, 'rb') as cached_file:
			logging.debug("Returning API response for %s" % (uri,))
			data = cached_file.read()
			return (200, headers, data)

	def tearDown(self):
		self._mock_disable()
	def _mock_disable(self):
		httpretty.disable()
