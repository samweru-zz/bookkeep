from books.controllers import sale
from books.models import *

import unittest

class TrxTestCase(unittest.TestCase):
	def setUp(self):
		self.trxNo = None

	def tearDown(self):
		Trx.objects.get(tno=self.trxNo).delete()
		for entry in Ledger.objects.filter(tno=self.trxNo):
			entry.delete()

	def test_trx(self):
		ltrx = sale.invoice(1200, "blah1")
		success = sale.receipt(ltrx.tno)
		self.trxNo = ltrx.tno

		self.assertIsInstance(ltrx, Trx)
		self.assertEqual(success, True)
