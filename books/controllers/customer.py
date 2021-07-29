from books.models import Catalogue
from books.models import Order as SalesOrder
from books.controllers import inventory as inv

from django.db import DatabaseError, transaction

import logging

logger = logging.getLogger(__name__)

class Order:
	def __init__(self, customer:str):
		self.descr = "Name: %s" % customer
		self.list = []
		self.trxNo = None

	def addItem(self, cat: Catalogue, units: int):
		self.list.append({"cat":cat, "units":units})

	def getTotalPrice(self):
		tt_amt = 0
		for item in self.list:
			tt_amt += item.get("cat").price * item.get("units")

		return tt_amt

	def create(self, trxNo:str):
		try:
			with transaction.atomic():
				if self.trxNo is None:
					for item in self.list:
						stock_item = inv.subtract(item.get("cat"), item.get("units"))
						order = SalesOrder(tno=trxNo, item=stock_item, units=item.get("units"))
						order.save()
						trxNo = trxNo
		except DatabaseError as e:
			logger.error(e)


