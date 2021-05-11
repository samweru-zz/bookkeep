from books.models import *
from bookkeep.util.number import Number 
from django.db import DatabaseError, transaction
from django.utils.crypto import get_random_string

from ruler import Ruler

import logging

logger = logging.getLogger(__name__)

def transfer(tno: str, token: str, amt: float):
	trxType = TrxType.objects.get(token=token)

	debit = Coa.objects.get(alias=trxType.dr.alias)
	credit = Coa.objects.get(alias=trxType.cr.alias)

	return Trx(tno=tno, dr=debit, cr=credit, amt=amt)
	
def prepSaleWithTax(amt, descr):
	cfgSaleTax = TrxCfg.objects.get(token="prepare.sale.tax")
	rruler = Ruler(cfgSaleTax.rules)
	taxRate = float(rruler.withHas("tax"))
	
	taxAmt, netSaleAmt = Number(amt).alloc(taxRate)

	trxNo = get_random_string().upper()

	try:
		with transaction.atomic():
			TrxLog(tno=trxNo, tt_amt=amt, descr=descr).save()
			transfer(tno=trxNo, token="prepare.sale", amt=netSaleAmt).save()
			transfer(tno=trxNo, token="prepare.sale.tax", amt=taxAmt).save()
	except DatabaseError as e:
		logger.error(e)