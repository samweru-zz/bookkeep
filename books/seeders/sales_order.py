from books.models import *
from books.controllers import accountant as acc
from books.controllers.customer import  Order as SaleOrder
from books.controllers import sale

from django.db import DatabaseError, transaction

import random
import logging

logger = logging.getLogger(__name__)

def getCatalogue():
	items = ["Computer Paper", "Lead pencil", "Computer Paper",
		"Ball Points", "Writing pad", "Stamp", "Sharpner Steadler",
		"Rubber Pelican", "Stamp Pad Pelican", "Box File A4",
		"Highlighter Pelican", "Glu Stick", "Binding Adhesive Tape",
		"Binding Plastic Sheet", "Brown Paper Sheet", "Calculator Casio",
		"Stapler Fine"]
	cat = Catalogue(name=random.choice(items), price=random.randint(250, 750))
	cat.save()
	return cat

def getStock(cat:Catalogue, trxNo:str):
	units = random.randint(10, 50)
	cost = random.randint(90, 200)
	stock = Stock(tno=trxNo, 
					code=acc.getCode(), 
					cat=cat, 
					unit_bal=units, 
					unit_total=units, 
					unit_cost=cost)
	stock.save()
	return stock

def getSalesOrder(item_count:int):
	try:
		with transaction.atomic():
			trxNo = acc.getTrxNo("SAL")
			so = SaleOrder()
			for i in range(item_count):
				cat = getCatalogue()
				stock = getStock(cat=cat, trxNo=trxNo)
				so.addItem(cat=cat, units=random.randint(5,15))
				
			so.saveWithTrxNo(trxNo)
			return so
	except DatabaseError as e:
		logger.error(e)

def newSale(item_count:int):
	try:
		with transaction.atomic():
			so = getSalesOrder(item_count=item_count)
			trx = sale.invoice(order=so, descr="Invoice No.: INV%s" % acc.getCode())
			sale.receipt(trxNo=trx.tno, amt=so.getTotalPrice())

			return True
	except DatabaseError as e:
		logger.error(e)

		return False