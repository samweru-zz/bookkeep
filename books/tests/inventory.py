from books.models import *
from freezegun import freeze_time
from django.test import TransactionTestCase
from django.test import TestCase
from django.db import DatabaseError, transaction

from books.controllers.customer import  Order as SaleOrder
from books.controllers import accountant as acc
from books.controllers import sale
from books.seeders import sales_order as so

import moment
import json
import unittest
import random
import datetime
import logging

logger = logging.getLogger(__name__)

class InventoryTestCase(TestCase):
	def setUp(self):
		self.trxNo = acc.getTrxNo("INV")

	def test_so(self):
		total_price = 0
		total_cost = 0

		try:
			with transaction.atomic():
				salesOrder = SaleOrder()
				for x in range(2):
					units = random.randint(1,10)
					cat = so.getCatalogue(created_at=datetime.datetime.now())
					stock = so.getStock(cat=cat, trxNo=self.trxNo, created_at=datetime.datetime.now())
					salesOrder.addItem(cat=cat, units=units)
					total_cost += units * stock.unit_cost
					total_price += units * stock.cat.price

				self.assertEqual(total_price, salesOrder.getTotalPrice())

				self.assertTrue(salesOrder.saveWithTrxNo(self.trxNo))

				self.assertEqual(total_cost, salesOrder.getTotalCost())

				trx = sale.invoice(order=salesOrder, descr="Stationery")

				self.assertTrue(sale.receipt(trxNo=self.trxNo, amt=salesOrder.getTotalPrice()))
		except DatabaseError as e:
			logger.error(e)
		except Exception as e:
			logger.error(e)

	def tearDown(self):
		pass