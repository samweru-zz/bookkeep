from books.models import *
from django.db import DatabaseError, transaction

import logging

logger = logging.getLogger(__name__)

def transfer(dr: Coa, cr: Coa, amt, descr):
	debit = Coa.objects.get(alias=dr)
	credit = Coa.objects.get(alias=cr)

	trx = Trx(dr=debit, cr=credit, amt=amt, descr=descr)
	trx.save()

def prepSaleWithTax(amt, descr):
	saleTrxType = TrxType.objects.get(token="prepare.sale")
	saleTrxTypeTax = TrxType.objects.get(token="prepare.sale.tax")

	try:
		with transaction.atomic():
			saleTrx = Trx(dr=saleTrxType.dr, cr=saleTrxType.cr, amt=amt, descr=descr)
			saleTrxType = Trx(dr=saleTrxTypeTax.dr, cr=saleTrxTypeTax.cr, amt=amt, descr=descr)
			saleTrx.save()
			saleTrxType.save()
	except DatabaseError as e:
		logger.error(e)