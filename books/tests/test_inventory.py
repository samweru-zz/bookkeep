from books.models import *
from freezegun import freeze_time
from django.test import TransactionTestCase

from books.controllers.customer import  Order as SaleOrder
from books.controllers import accountant as acc
from books.controllers import sale

import moment
import json
import unittest

# class InventoryTestCase(TransactionTestCase):
class InventoryTestCase(unittest.TestCase):
	def setUp(self):
		self.trxNo = acc.getTrxNo("INV")

	def test_so(self):
		# print(TrxType.objects.all())

		c1 = Catalogue(name="Paper Punch", price=2500)
		c2 = Catalogue(name="Staplers", price=1000)
		c1.save()
		c2.save()

		s1 = Stock(tno=self.trxNo, code=acc.getCode(), cat=c1, 
					unit_bal=10, unit_total=10, unit_cost=100)
		s2 = Stock(tno=self.trxNo, code=acc.getCode(), cat=c2,
					unit_bal=20, unit_total=20, unit_cost=200)
		s1.save()
		s2.save()

		so = SaleOrder()
		so.addItem(cat=c1, units=2)
		so.addItem(cat=c2, units=3)

		self.assertEqual(8000, so.getTotalPrice())

		self.assertTrue(so.saveWithTrxNo(self.trxNo))

		self.assertEqual(800, so.getTotalCost())

		trx = sale.invoice(order=so, descr="Stationery")

		self.assertTrue(sale.receipt(trxNo=self.trxNo, amt=so.getTotalPrice()))

	def tearDown(self):
		pass