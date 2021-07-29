from books.models import Catalogue
from books.models import Order as ItemOrder
from books.controllers import inventory as inv

from django.db import DatabaseError, transaction

import logging

logger = logging.getLogger(__name__)

class Order:
	def __init__(self, trxNo:str=None):
		self.trxNo = trxNo
		self.catList = []
		self.itemList = []

	def addItem(self, cat:Catalogue, units:int):
		self.catList.append({"cat":cat, "units":units})

	def getTotalPrice(self):
		tt_amt = 0
		for item in self.catList:
			tt_amt += item.get("cat").price * item.get("units")

		return tt_amt

	def getTotalCost(self):
		tt_cost = 0
		for order in self.itemList:
			tt_cost += order.item.unit_cost * order.units

		return tt_cost

	def saveWithTrxNo(self, trxNo:str):
		try:
			with transaction.atomic():
				if self.trxNo is None:
					for item in self.catList:
						stock_item = inv.subtract(item.get("cat"), item.get("units"))
						order = ItemOrder(tno=trxNo, item=stock_item, units=item.get("units"))
						order.save()
						self.itemList.append(order)
						self.trxNo = trxNo
						
					return True
			return False
		except DatabaseError as e:
			logger.error(e)

			return False

	def findByTrxNo(trxNo:str):
		items = ItemOrder.objects.filter(tno=trxNo)

		salesOrder = None
		if(items.count() > 0):
			salesOrder = Order(trxNo)
			salesOrder.itemList = items
			for order in items:
				salesOrder.addItem(order.item.cat, order.units)

		return salesOrder						


