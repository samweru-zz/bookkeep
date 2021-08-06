from books.models import *

from django.utils.crypto import get_random_string

import random, string

def getTrxNo(prefix):
	random = get_random_string().upper()
	return prefix + random

def withTrxNo(prefix, trxNo):
	return prefix + trxNo[3:]

def getBalStatus(amt, trx: Trx):
	if(amt is None):
		amt = trx.qamt

	if(amt > trx.bal):
		raise Exception("Residual amount cannot be greater than balance!")

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

def reverse(entry: Ledger, amt: float):
	credit = Coa.objects.get(id=entry.cr.id)
	debit = Coa.objects.get(id=entry.dr.id)

	return Ledger(tno=entry.tno, dr=credit, cr=debit, amt=amt)

def getCode(length:int=8):
 	return ''.join(random.choices(string.ascii_letters + string.digits, k=length)).upper()