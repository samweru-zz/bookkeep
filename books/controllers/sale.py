from books.models import *
from bookkeep.util.number import Number
from bookkeep.util.ruler import Ruler
from books.controllers import accountant as acc
from books.controllers import inventory as inv

from django.db import DatabaseError, transaction


import logging

logger = logging.getLogger(__name__)

#invoice
# def invoice(amt, cogs, descr):
def invoice(cat: Catalogue, units: int, descr: str):
	trxNo = acc.getTrxNo("INV")

	trx = None

	try:
		with transaction.atomic():
			trx = Trx(tno=trxNo, qamt=amt, bal=amt, descr=descr)
			trx.save()
			acc.transfer(trxNo=trxNo, token="prepare.sale", amt=netSaleAmt).save()
	except DatabaseError as e:
		logger.error(e)

	return trx

#sales receipt
def receipt(trxNo: str, amt: float=None):
	trx = Trx.objects.get(tno=trxNo)
	bal, status = acc.getBalStatus(amt, trx)
	taxAmt = getSaleTax(amt=amt)

	rtrxNo = acc.withTrxNo("REC", trxNo)

	try:
		with transaction.atomic():
			trx.bal = bal
			trx.status = status
			trx.save()

			acc.transfer(trxNo=rtrxNo, token="apply.sale", amt=amt).save()
			acc.transfer(trxNo=rtrxNo, token="apply.sale.tax", amt=taxAmt).save()
			acc.transfer(trxNo=rtrxNo, token="apply.cogs", amt=cogs).save()

		return True
	except DatabaseError as e:
		logger.error(e)

		return False

# def getSaleTaxRatio(amt:float):
def getSaleTax(amt:float):
	cfgSaleTax = TrxCfg.objects.get(token="sale.tax")
	rules = Ruler(cfgSaleTax.rules)
	taxRate = float(rules.get("tax"))

	# return Number(amt).alloc(taxRate)
	return amt * taxRate

