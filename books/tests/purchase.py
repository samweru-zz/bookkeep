from books.models import *
from freezegun import freeze_time
from django.test import TestCase

from books.controllers.inventory import  Requisition as InvReq
from books.controllers import accountant as acc
from books.controllers import purchase as pur

import moment
import json
import unittest

class PurchaseTestCase(TestCase):
# class PurchaseTestCase(unittest.TestCase):
	def setUp(self):
		self.trxNo = acc.getTrxNo("INV")

	def test_po(self):
		c1 = Catalogue(name="RAM Memory", price=2500)
		c2 = Catalogue(name="Keyboard", price=1000)
		c1.save()
		c2.save()

		req = InvReq(None)
		req.add(cat=c1, units=25, unit_cost=350)
		req.add(cat=c2, units=15, unit_cost=125)

		self.assertTrue(req.saveWithTrxNo(self.trxNo))
		self.assertEqual(10625, req.getTotalCost())

		# req = InvReq.findByTrxNo(self.trxNo)
		trx = pur.order(req=req, descr="Computer Accessories")
		trx.save()
		self.assertTrue(pur.pay(trxNo=self.trxNo, amt=10625))

	def tearDown(self):
		pass