from books.models import *
from freezegun import freeze_time
from django.test import TestCase
from django.db import DatabaseError, transaction

from books.controllers.inventory import  Requisition as InvReq
from books.controllers import accountant as acc
from books.controllers import purchase as pur
from books.seeders import purchase_order as po

import moment
import json
import unittest
import datetime
import logging
import random

logger = logging.getLogger(__name__)

class PurchaseTestCase(TestCase):
	def setUp(self):
		self.trxNo = acc.getTrxNo("PUR")

	def test_po(self):
		try:
			with transaction.atomic():
				total_costs = 0

				req = InvReq(None)
				for x in range(2):
					units = random.randint(15,35)
					unit_cost = random.randint(100,500)
					cat = po.getCatalogue(created_at=datetime.datetime.now())
					req.add(cat=cat, units=units, unit_cost=unit_cost)
					total_costs += units * unit_cost

				self.assertTrue(req.saveWithTrxNo(self.trxNo))
				self.assertEqual(total_costs, req.getTotalCost())

				pur.order(req=req, descr="Computer Accessories").save()

				self.assertTrue(pur.pay(trxNo=self.trxNo, amt=total_costs))
		except DatabaseError as e:
			logger.error(e)
		except Exception as e:
			logger.error(e)

	def tearDown(self):
		pass