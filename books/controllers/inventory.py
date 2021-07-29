from books.models import *

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

def add(cat: Catalogue, units: int, unit_cost: float):
	stocks = Stock.objects.filter(cat__id=cat.id, status="Active")
	stock = Stock(cat=cat, bal=units, total=units, unit_cost=unit_cost)
	if(stocks.count() == 0):
		stock.status = "Active"

	stock.save()

	return stock