from books.models import *
from books.controllers import accountant

from django.db import DatabaseError, transaction

import logging

logger = logging.getLogger(__name__)

def order(amt, descr):
	trxNo = accountant.getTrxNo("PUR")

	trx = None

	try:
		with transaction.atomic():
			trx = Trx(tno=trxNo, qamt=amt, bal=amt, descr=descr)
			trx.save()
			accountant.transfer(trxNo=trxNo, token="prepare.purchase", amt=amt).save()
	except DatabaseError as e:
		logger.error(e)

	return trx

def pay(trxNo: str, amt: float=None):
	trx = Trx.objects.get(tno=trxNo)
	bal, status = accountant.getBalStatus(amt, trx)

	try:
		with transaction.atomic():
			trx.bal = bal
			trx.status = status
			trx.save()
			accountant.transfer(trxNo=trxNo, token="pay.purchase", amt=amt).save()

		return True
	except DatabaseError as e:
		logger.error(e)

		return False