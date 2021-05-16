from books.models import *
from bookkeep.util.number import Number
from bookkeep.util.ruler import Ruler
from books.controllers import accountant

from django.db import DatabaseError, transaction
from django.utils.crypto import get_random_string

import logging

logger = logging.getLogger(__name__)

def invoice(amt, descr):
	taxAmt, netSaleAmt = getSaleVsTaxAlloc(amt=amt)

	trxNo = get_random_string().upper()

	trx = None

	try:
		with transaction.atomic():
			trx = Trx(tno=trxNo, qamt=amt, bal=amt, descr=descr)
			trx.save()
			accountant.transfer(trxNo=trxNo, token="prepare.sale", amt=netSaleAmt).save()
			accountant.transfer(trxNo=trxNo, token="prepare.sale.tax", amt=taxAmt).save()
	except DatabaseError as e:
		logger.error(e)

	return trx

def receipt(trxNo: str, amt: float=None):
	trx = Trx.objects.get(tno=trxNo)

	if(amt is None):
		amt = trx.qamt

	if(amt > trx.bal):
		raise Exception("Residual sale amount cannot be greater than balance!")

	taxAmt, netSaleAmt = getSaleVsTaxAlloc(amt=amt)
	bal = trx.bal - amt

	status = "Pending"
	if(bal == 0):
		status = "Final"

	try:
		with transaction.atomic():
			trx.bal = bal
			trx.status = status
			trx.save()
			accountant.transfer(trxNo=trxNo, token="apply.sale", amt=netSaleAmt).save()
			accountant.transfer(trxNo=trxNo, token="apply.sale.tax", amt=taxAmt).save()

		return True
	except DatabaseError as e:
		logger.error(e)

		return False

def getSaleVsTaxAlloc(amt:float):
	cfgSaleTax = TrxCfg.objects.get(token="sale.tax")
	rules = Ruler(cfgSaleTax.rules)
	taxRate = float(rules.get("tax"))

	return Number(amt).alloc(taxRate)

