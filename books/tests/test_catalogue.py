from books.models import *
from freezegun import freeze_time
from django.test import TransactionTestCase
# from django.test import TestCase

import moment
import json
import unittest

class CatalogueTestCase(TransactionTestCase):
# class CatalogueTestCase(unittest.TestCase):
# class CatalogueTestCase(TestCase):
	def setUp(self):
		pass

	@freeze_time("2012-01-14")	
	def test_new_items(self):
		items = json.load(open("fixtures/catalogue.json"))
		for item in items:
			cat = Catalogue()
			fields = item.get("fields")
			for key in fields.keys():
				setattr(cat, key, fields.get(key))
				
			cat.save()

		self.assertTrue(True)

	def tearDown(self):
		pass