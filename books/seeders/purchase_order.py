from books.models import *
from books.controllers.inventory import  Requisition as InvReq
from books.controllers import accountant as acc
from books.controllers import purchase as pur

from django.db import DatabaseError, transaction

import random
import logging

logger = logging.getLogger(__name__)

def getCatalogue():
	items = ["Case", "Motherboard", "CPU [Processor]",
		"GPU [Graphics Card]", "RAM [Memory]", "Storage Device (SSD, NVME SSD, HDD)",
		"Cooling (CPU, Chassis)", "PSU [Power Supply Unit]", "Display device, Monitor",
		"Operating System [OS]","Input Devices, Mouse, Keyboard"]

	cat = Catalogue(name=random.choice(items), price=random.randint(1500, 3500))
	cat.save()
	return cat

def getInvReq(cat_count:int):
	req = InvReq(None)
	for i in range(cat_count):
		cat = getCatalogue()
		req.add(cat=cat, units=random.randint(25,55), unit_cost=random.randint(750, 1450))
	req.saveWithTrxNo(acc.getTrxNo("PUR"))
	return req

def getPurchaseOrder(cat_count:int):
	try:
		with transaction.atomic():
			req = getInvReq(cat_count=cat_count)
			trx = pur.order(req=req, descr="Purchase Order: PUR%s" % acc.getCode())
			pur.pay(trxNo=trx.tno, amt=req.getTotalCost())

			return True
	except DatabaseError as e:
		logger.error(e)

		return False