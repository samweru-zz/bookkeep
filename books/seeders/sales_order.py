from books.models import *
from books.controllers import accountant as acc
from books.controllers.customer import  Order as SaleOrder
from books.controllers import sale

from django.db import DatabaseError, transaction

import random
import logging
import datetime

logger = logging.getLogger(__name__)

def getCatalogue(created_at:datetime.datetime=None):
	items = ["Computer Paper", "Lead pencil", "Computer Paper",
		"Ball Points", "Writing pad", "Stamp", "Sharpner Steadler",
		"Rubber Pelican", "Stamp Pad Pelican", "Box File A4",
		"Highlighter Pelican", "Glu Stick", "Binding Adhesive Tape",
		"Binding Plastic Sheet", "Brown Paper Sheet", "Calculator Casio",
		"Stapler Fine"]

	cat = Catalogue(name=random.choice(items), 
					price=random.randint(250, 750))

	if created_at is not None:
		cat.created_at = created_at

	cat.save()

	return cat

def getStock(cat:Catalogue, trxNo:str, created_at:datetime.datetime=None):
	units = random.randint(10, 50)
	cost = random.randint(90, 200)
	stock = Stock(tno=trxNo, 
					code=acc.getCode(), 
					cat=cat, 
					unit_bal=units, 
					unit_total=units, 
					unit_cost=cost)

	if created_at is not None:
		stock.created_at = created_at

	stock.save()

	return stock

def getSalesOrder(item_count:int, created_at:datetime.datetime=None):
	try:
		with transaction.atomic():
			trxNo = acc.getTrxNo("INV")
			so = SaleOrder()
			for i in range(item_count):
				cat = getCatalogue(created_at=created_at)
				stock = getStock(cat=cat, trxNo=trxNo, created_at=created_at)
				so.addItem(cat=cat, units=random.randint(5,15))
				
			so.saveWithTrxNo(trxNo=trxNo, created_at=created_at)

			return so
	except DatabaseError as e:
		logger.error(e)

def newSale(item_count:int, created_at:datetime.datetime=None):
	try:
		with transaction.atomic():
			so = getSalesOrder(item_count=item_count, created_at=created_at)
			trx = sale.invoice(order=so, 
								descr="Invoice No.: INV%s" % acc.getCode(),
								created_at=created_at)

			sale.receipt(trxNo=trx.tno, amt=so.getTotalPrice(), created_at=created_at)

			return True
	except DatabaseError as e:
		logger.error(e)