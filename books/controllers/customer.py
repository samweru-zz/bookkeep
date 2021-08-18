from books.models import Catalogue
from books.models import Order as ItemOrder
from books.controllers import inventory as inv

from django.db import DatabaseError, transaction

import logging
import datetime

logger = logging.getLogger(__name__)

class Order:
	def __init__(self, trxNo:str=None):
		self.trxNo = trxNo
		self.catList = []

	def addItem(self, cat:Catalogue, units:int):
		self.catList.append({"cat":cat, "units":units})

	def getTotalPrice(self):
		tt_amt = 0
		for item in self.catList:
			tt_amt += item.get("cat").price * item.get("units")

		return tt_amt

	def getTotalCost(self):
		if self.trxNo is not None:
			orders = ItemOrder.objects.filter(tno=self.trxNo)

			tt_cost = 0
			for order in orders:
				tt_cost += order.item.unit_cost * order.units

			return tt_cost
		else:
			return None

	def isEmpty(self):
		return not len(self.catList)>0

	def saveWithTrxNo(self, trxNo:str, created_at:datetime.datetime=None):
		try:
			with transaction.atomic():
				if self.trxNo is None:
					self.trxNo = trxNo
					for item in self.catList:
						stock_item = inv.subtract(item.get("cat"), item.get("units"))
						order = ItemOrder(tno=trxNo, 
											item=stock_item, 
											units=item.get("units"))

						if created_at is not None:
							order.created_at=created_at
							
						order.save()
						
					return True
			return False
		except DatabaseError as e:
			self.trxNo = None

			return False

	def save(self, created_at:datetime.datetime=None):
		try:
			with transaction.atomic():
				if self.trxNo is not None:
					for item in self.catList:
						if "oid" not in item.keys():
							stock_item = inv.subtract(item.get("cat"), item.get("units"))
							order = ItemOrder(tno=self.trxNo, 
												item=stock_item, 
												units=item.get("units"))

							if created_at is not None:
								order.created_at=created_at

							order.save()
						
					return True
			return False
		except DatabaseError as e:
			return False

	def updateWithStatus(self, status):
		try:
			with transaction.atomic():
				for item in self.catList:
					if "oid" in item.keys():
						order = ItemOrder.objects.get(id=item.get("oid"))
						if order.status != "Final":
							order.status = status
							order.save()

				return True
		except DatabaseError as e:
			return False

	def findByTrxNo(trxNo:str):
		items = ItemOrder.objects.filter(tno=trxNo)

		salesOrder = Order()
		if(items.count() > 0):
			salesOrder = Order(trxNo)
			for order in items:
				if order.status != "Reverted":
					salesOrder.catList.append({

						"cat":order.item.cat, 
						"units":order.units,
						"oid":order.id
					})

		return salesOrder