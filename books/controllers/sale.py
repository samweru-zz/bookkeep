from books.models import *
from bookkeep.util.number import Number
from bookkeep.util.ruler import Ruler
from books.controllers import accountant as acc
from books.controllers.customer import Order as SalesOrder

from django.db import DatabaseError, transaction

import logging
import datetime

logger = logging.getLogger(__name__)

#invoice
def invoice(order: SalesOrder, descr: str, created_at:datetime.datetime=None):
	if order.trxNo is None:
		raise("Order Trx No is empty!")

	trxNo = order.trxNo
	price = order.getTotalPrice()

	try:
		with transaction.atomic():
			trx = acc.newTrx(trxNo=trxNo, amt=price, descr=descr, created_at=created_at)
			trx.save()
			acc.newEntry(trxNo=trxNo, 
							token="prepare.sale", 
							amt=price, 
							created_at=created_at).save()

			return trx
	except DatabaseError as e:
		logger.error(e)

#sales receipt
def receipt(trxNo:str, amt:float=None, created_at:datetime.datetime=None):
	trx = Trx.objects.get(tno=trxNo)
	bal, status = acc.getBalStatus(amt, trx)
	tax = getSaleTax(amt=amt)

	order = SalesOrder.findByTrxNo(trxNo)
	cogs = order.getTotalCost()

	rtrxNo = acc.withTrxNo("REC", trxNo)

	try:
		with transaction.atomic():
			if trx.status == "Pending":
				trx.bal = bal
				trx.status = status
				trx.save()

				acc.newEntry(trxNo=rtrxNo, token="apply.sale", amt=amt, created_at=created_at).save()
				acc.newEntry(trxNo=rtrxNo, token="apply.sale.tax", amt=tax, created_at=created_at).save()
				acc.newEntry(trxNo=rtrxNo, token="apply.cogs", amt=cogs, created_at=created_at).save()

				return True
		return False
	except DatabaseError as e:
		logger.error(e)

		return False

#sales return
def returns(so:SalesOrder, created_at:datetime.datetime=None):
	trxNo = so.trxNo
	oTrxNo = acc.withTrxNo("INV", trxNo)
	trx = Trx.objects.filter(tno=oTrxNo).first()

	try:
		with transaction.atomic():
			total_price = so.getTotalPrice()
			total_cost = so.getTotalCost()

			trx.bal = trx.bal - total_price
			trx.save()

			acc.newEntry(trxNo=trxNo, token="apply.sale-return", amt=total_price, created_at=created_at).save()
			acc.newEntry(trxNo=trxNo, token="reverse.cogs", amt=total_cost, created_at=created_at).save()

			return trx
	except DatabaseError as e:
		logger.error(e)

def getSaleTax(amt:float):
	cfgSaleTax = TrxCfg.objects.get(token="sale.tax")
	rules = Ruler(cfgSaleTax.rules)
	taxRate = float(rules.get("tax"))

	return amt * taxRate