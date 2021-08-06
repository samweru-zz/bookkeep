from django.db import models
from datetime import datetime

class Period(models.Model):
	pno = models.CharField(max_length=200)
	start_date = models.DateTimeField(auto_now=True)
	end_date = models.DateTimeField()

class Coa(models.Model):
	name = models.CharField(max_length=200)
	code = models.IntegerField(default=0)
	alias = models.CharField(max_length=200)
	token = models.CharField(max_length=200)
	rules = models.TextField()

class Trx(models.Model):
	tno = models.CharField(max_length=200)
	descr = models.TextField(default="N/A")
	qamt = models.FloatField() #total amount
	bal = models.FloatField(default=0) #balance
	status = models.CharField(max_length=200, default="Pending")
	created_at = models.DateTimeField(default=datetime.now, editable=True)
	# created_at = models.DateTimeField(auto_now=True)

class Schedule(models.Model):
	tno = models.CharField(max_length=200)
	descr = models.TextField(default="N/A")
	amt = models.FloatField()
	status = models.CharField(max_length=200, default="Pending")
	created_at = models.DateTimeField(default=datetime.now)
	# created_at = models.DateTimeField(auto_now=True)

class Ledger(models.Model):
	tno = models.CharField(max_length=200)
	dr = models.ForeignKey(Coa, related_name="TrxDebit", on_delete=models.DO_NOTHING)
	cr = models.ForeignKey(Coa, related_name="TrxCredit", on_delete=models.DO_NOTHING)
	amt = models.FloatField()
	created_at = models.DateTimeField(default=datetime.now)
	# created_at = models.DateTimeField(auto_now=True)

class TrxType(models.Model):
	token = models.CharField(max_length=200)
	dr = models.ForeignKey(Coa, related_name="TrxTypeDebit", on_delete=models.DO_NOTHING)
	cr = models.ForeignKey(Coa, related_name="TrxTypeCredit", on_delete=models.DO_NOTHING)

class TrxCfg(models.Model):
	token = models.CharField(max_length=200)
	rules = models.TextField()
	descr = models.TextField(default="N/A");
	status = models.CharField(max_length=200, default="Active")

class TrxAlloc(models.Model):
	acc = models.ForeignKey(Coa, on_delete=models.DO_NOTHING)
	amt = models.FloatField() #change to balance
	limit = models.FloatField() #limit of allocation
	created_at = models.DateTimeField(auto_now=True)

class Catalogue(models.Model):
	name = models.CharField(max_length=200)
	price = models.FloatField() #change to balance
	descr = models.TextField(default="N/A")
	status = models.CharField(max_length=200, default="Active")
	created_at = models.DateTimeField(default=datetime.now)

class Stock(models.Model):
	tno = models.CharField(max_length=200)
	cat = models.ForeignKey(Catalogue, related_name="XCatalogue", on_delete=models.DO_NOTHING)
	code = models.CharField(max_length=200)
	unit_bal = models.IntegerField(default=0)
	unit_total = models.IntegerField(default=0)
	unit_cost = models.FloatField()
	status = models.CharField(max_length=200, default="Pending")
	created_at = models.DateTimeField(default=datetime.now)

class Order(models.Model):
	tno = models.CharField(max_length=200)
	item = models.ForeignKey(Stock, on_delete=models.DO_NOTHING)
	units = models.IntegerField(default=0)
	status = models.CharField(max_length=200, default="Pending")
	created_at = models.DateTimeField(auto_now=True)
