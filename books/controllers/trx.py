from books.models import *
from bookkeep.util.number import Number 
from django.db import DatabaseError, transaction
from django.utils.crypto import get_random_string

from ruler import Ruler

import logging

logger = logging.getLogger(__name__)

def transfer(trxNo: str, token: str, amt: float):
	trxType = TrxType.objects.get(token=token)

	debit = Coa.objects.get(alias=trxType.dr.alias)
	credit = Coa.objects.get(alias=trxType.cr.alias)

	return Trx(tno=trxNo, dr=debit, cr=credit, amt=amt)
	
def prepSale(amt, descr):
	taxAmt, netSaleAmt = getSaleVsTaxAlloc(amt=amt)

	trxNo = get_random_string().upper()

	try:
		with transaction.atomic():
			TrxLog(tno=trxNo, qamt=amt, bal = amt, descr=descr).save()
			transfer(trxNo=trxNo, token="prepare.sale", amt=netSaleAmt).save()
			transfer(trxNo=trxNo, token="prepare.sale.tax", amt=taxAmt).save()
	except DatabaseError as e:
		logger.error(e)

def makeSale(trxNo: str, amt: float=None):
	log = TrxLog.objects.get(tno=trxNo)

	if(amt is None):
		amt = log.qamt

	if(amt > log.bal):
		raise Exception("Residual sale amount cannot be greater than balance!")

	taxAmt, netSaleAmt = getSaleVsTaxAlloc(amt=amt)
	bal = log.bal - amt

	status = "Pending"
	if(bal == 0):
		status = "Final"

	try:
		with transaction.atomic():
			log.bal = bal
			log.status = status
			log.save()
			transfer(trxNo=trxNo, token="apply.sale", amt=netSaleAmt).save()
			transfer(trxNo=trxNo, token="apply.sale.tax", amt=taxAmt).save()
	except DatabaseError as e:
		logger.error(e)

def getSaleVsTaxAlloc(amt:float):
	cfgSaleTax = TrxCfg.objects.get(token="sale.tax")
	rules = Ruler(cfgSaleTax.rules)
	taxRate = float(rules.get("tax"))

	return Number(amt).alloc(taxRate)

