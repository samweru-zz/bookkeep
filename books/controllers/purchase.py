from books.models import *
from books.controllers import accountant as acc
from books.controllers.inventory import Requisition as InvReq

from django.db import DatabaseError, transaction

import logging
import datetime

logger = logging.getLogger(__name__)

#local purchase order
def order(req: InvReq, descr:str, created_at:datetime.datetime=None):
	trxNo = req.trxNo
	amt = req.getTotalCost()

	try:
		with transaction.atomic():
			trx = acc.newTrx(trxNo=trxNo, amt=amt, descr=descr, created_at=created_at)
			trx.save()
			acc.newEntry(trxNo=trxNo, 
							token="prepare.purchase", 
							amt=amt, 
							created_at=created_at).save()

			return trx
	except DatabaseError as e:
		logger.error(e)

#payment receipt
def pay(trxNo: str, amt: float=None, created_at:datetime.datetime=None):
	trx = Trx.objects.get(tno=trxNo)
	bal, status = acc.getBalStatus(float(amt), trx)

	ptrxNo = acc.withTrxNo("PAY", trxNo)

	try:
		with transaction.atomic():
			trx.bal = bal
			trx.status = status
			trx.save()
			acc.newEntry(trxNo=ptrxNo, 
							token="pay.purchase", 
							amt=amt, 
							created_at=created_at).save()

		return True
	except DatabaseError as e:
		logger.error(e)

		return False