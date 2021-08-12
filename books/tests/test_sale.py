from books.controllers import sale
from books.models import *

import unittest
# import pytest

class TrxTestCase(unittest.TestCase):
	def setUp(self):
		pass
		# self.trxNo = None

	def tearDown(self):
		# Trx.objects.get(tno=self.trxNo).delete()
		# for entry in Ledger.objects.filter(tno=self.trxNo):
		# 	entry.delete()
		pass

	# @pytest.mark.django_db
	def test_trx(self):
		# c1 = Catalogue.objects.get(id=13)

		# print(c1.name)
		# ltrx = sale.invoice(1200, "blah1")
		# success = sale.receipt(ltrx.tno)
		# self.trxNo = ltrx.tno

		# self.assertIsInstance(ltrx, Trx)
		# self.assertEqual(success, True)
		pass
