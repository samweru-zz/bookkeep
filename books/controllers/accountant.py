from books.models import *

from django.utils.crypto import get_random_string


import random, string
import datetime

def getTrxNo(prefix):
	random = get_random_string().upper()
	return prefix + random

def withTrxNo(prefix, trxNo):
	return prefix + trxNo[3:]

def getBalStatus(amt:float, trx: Trx):
	if(amt is None):
		amt = trx.qamt

	if(amt > trx.bal):
		raise Exception("Residual amount cannot be greater than balance!")

	bal = trx.bal - amt

	status = "Pending"
	if(bal == 0):
		status = "Final"

	return bal, status

def newTrx(trxNo:str, amt:float, descr:str, created_at:datetime.datetime=None):
	trx = Trx(tno=trxNo, qamt=amt, bal=amt, descr=descr)
	
	if created_at is not None:
		trx.created_at = created_at

	return trx
	 

def newEntry(trxNo:str, token:str, amt:float, created_at:datetime.datetime=None):
	trxType = TrxType.objects.get(token=token)

	debit = Coa.objects.get(alias=trxType.dr.alias)
	credit = Coa.objects.get(alias=trxType.cr.alias)

	entry = Ledger(tno=trxNo, dr=debit, cr=credit, amt=amt)

	if created_at is not None:
		entry.created_at = created_at	

	return entry

def revEntry(entry: Ledger, amt: float, created_at:datetime.datetime=None):
	credit = Coa.objects.get(id=entry.cr.id)
	debit = Coa.objects.get(id=entry.dr.id)

	trxNo = withTrxNo("REV", entry.tno)

	entry = Ledger(tno=trxNo, dr=credit, cr=debit, amt=amt)

	if created_at is not None:
		entry.created_at = created_at

	return entry

def getCode(length:int=8):
 	return ''.join(random.choices(string.ascii_letters + string.digits, k=length)).upper()