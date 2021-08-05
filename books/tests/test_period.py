from books.models import *
from freezegun import freeze_time
from django.test import TestCase

import moment
# import unittest

# class PeriodTestCase(unittest.TestCase):
class PeriodTestCase(TestCase):
	def setUp(self):
		pass

	@freeze_time("2012-01-14")	
	def test_new_period(self):
		period = Period(start_date=moment.date("-2 years").date, end_date=moment.date("-1 year").date)
		period.save()
		self.assertIsInstance(period, Period)

	def tearDown(self):
		pass