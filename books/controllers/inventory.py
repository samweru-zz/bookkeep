from books.models import Stock, Catalogue
from books.controllers import accountant as acc

from django.db import DatabaseError, transaction

import logging

logger = logging.getLogger(__name__)

def next(cat: Catalogue):
	return Stock.objects.filter(cat__id=cat.id, status="Pending").order_by("-id").last()

def subtract(cat: Catalogue, units: int):
	try:
		with transaction.atomic():
			if(Stock.objects.filter(cat=cat, status="Active").exists()):
				stock = Stock.objects.get(cat__id=cat.id, status="Active")
			else:
				stock = next(cat=cat)
				stock.status = "Active"

			if(units > stock.unit_bal):
				raise Exception("Number of units is unavailable!")

			stock.unit_bal = stock.unit_bal - units
			if(stock.unit_bal == 0):
				stock.status = "Final"

			stock.save()

			return stock
	except DatabaseError as e:
		logger.error(e)

		return None

class Order:
	def __init__(self, trxNo:str):
 		self.itemList = []
 		self.trxNo = trxNo

	def getActiveStockByCategory(cat: Catalogue):
		return Stock.objects.filter(cat__id=cat.id, status="Active")

	def add(self, cat: Catalogue, units: int, unit_cost: float):
		self.itemList.append({"cat":cat, "units":units, "unit_cost":unit_cost})

	def getTotalCost(self):
		tt_cost = 0
		for item in self.itemList:
			tt_cost += item.get("units") * item.get("unit_cost")

		return tt_cost


	def saveWithTrxNo(self, trxNo:str):
		try:
			if trxNo is not None:
				with transaction.atomic():
					for item in self.itemList:
						stock = Stock(cat=item.get("cat"), 
										code=acc.getCode(),
										tno=trxNo,
										unit_bal=item.get("units"), 
										unit_total=item.get("units"), 
										unit_cost=item.get("unit_cost"))

						"""
						If there are no other active stock batches, make current
						stock batch active
						"""
						stocks = Order.getActiveStockByCategory(item.get("cat"))
						if(stocks.count() == 0):
							stock.status = "Active"
							
						stock.save()

					self.trxNo = trxNo

					return True
			return False
		except DatabaseError as e:
			logger.error(e)

			return False

	def findByTrxNo(trxNo:str):
		invOrder = None
		# stocks = Stock.objects.filter(tno=trxNo)
		stocks = Stock.objects.filter(tno__contains=trxNo)
		if(stocks.count() > 0):
			invOrder = Order(trxNo)
			for stock in stocks:
				invOrder.add(cat=stock.cat,
								units=stock.unit_total,
								unit_cost=stock.unit_cost)

			return invOrder
		return None

