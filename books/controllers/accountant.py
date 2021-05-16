from books.models import *

from django.utils.crypto import get_random_string

def getTrxNo(prefix):
	random = get_random_string().upper()
	return prefix + random

def getBalStatus(amt, trx: Trx):
	if(amt is None):
		amt = trx.qamt

	if(amt > trx.bal):
		raise Exception("Residual sale amount cannot be greater than balance!")

	bal = trx.bal - amt

	status = "Pending"
	if(bal == 0):
		status = "Final"

	return bal, status


def transfer(trxNo: str, token: str, amt: float):
	trxType = TrxType.objects.get(token=token)

	debit = Coa.objects.get(alias=trxType.dr.alias)
	credit = Coa.objects.get(alias=trxType.cr.alias)

	return Ledger(tno=trxNo, dr=debit, cr=credit, amt=amt)