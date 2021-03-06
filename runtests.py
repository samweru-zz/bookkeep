#!/usr/bin/env python

import os
import unittest
import django
import warnings
from django.conf import settings

warnings.filterwarnings("ignore")
os.environ['DJANGO_SETTINGS_MODULE'] = 'bookkeep.settings'

# databases = settings.DATABASES

django.setup()

from books.tests.inventory import InventoryTestCase as InvTC
from books.tests.purchase import PurchaseTestCase as PurTC

def suite():
	suite = unittest.TestSuite()
	for cls_test_case in [InvTC, PurTC]:
		suite.addTest(unittest.TestLoader().loadTestsFromTestCase(cls_test_case))
	return suite

if __name__ == '__main__':	
	unittest.TextTestRunner().run(suite())