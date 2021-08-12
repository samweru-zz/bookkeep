#!/usr/bin/env python

import os
import unittest
import django
import warnings

warnings.filterwarnings("ignore")
os.environ['DJANGO_SETTINGS_MODULE'] = 'bookkeep.settings'
django.setup()

from books.tests.test_inventory import InventoryTestCase as InvTC
from books.tests.test_purchase import PurchaseTestCase as PurTC

def suite():
	suite = unittest.TestSuite()
	for cls_test_case in [InvTC, PurTC]:
		suite.addTest(unittest.TestLoader().loadTestsFromTestCase(cls_test_case))
	return suite

if __name__ == '__main__':	
	unittest.TextTestRunner().run(suite())