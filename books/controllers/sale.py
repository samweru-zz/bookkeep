from books.models import *
from bookkeep.util.number import Number
from bookkeep.util.ruler import Ruler
from books.controllers import accountant as acc
from books.controllers.customer import Order as SalesOrder

from django.db import DatabaseError, transaction

import logging

logger = logging.getLogger(__name__)

#invoice
def invoice(order: SalesOrder, descr: str):
	trx = None
	trxNo = acc.getTrxNo("INV")
	price = order.getTotalPrice()

	try:
		with transaction.atomic():
			trx = Trx(tno=trxNo, qamt=price, bal=price, descr=descr)
			trx.save()
			acc.transfer(trxNo=trxNo, token="prepare.sale", amt=price).save()
			# order.saveWithTrxNo(trxNo)
			# order.save()
	except DatabaseError as e:
		logger.error(e)

	return trx

#sales receipt
def receipt(trxNo: str, amt: float=None):
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

				acc.transfer(trxNo=rtrxNo, token="apply.sale", amt=amt).save()
				acc.transfer(trxNo=rtrxNo, token="apply.sale.tax", amt=tax).save()
				acc.transfer(trxNo=rtrxNo, token="apply.cogs", amt=cogs).save()

				return True
		return False
	except DatabaseError as e:
		logger.error(e)

		return False

def getSaleTax(amt:float):
	cfgSaleTax = TrxCfg.objects.get(token="sale.tax")
	rules = Ruler(cfgSaleTax.rules)
	taxRate = float(rules.get("tax"))

	return amt * taxRate