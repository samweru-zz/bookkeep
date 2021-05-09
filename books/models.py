from django.db import models

class Period(models.Model):
	start_date = models.DateTimeField(auto_now=True)
	end_date = models.DateTimeField()

class Coa(models.Model):
	name = models.CharField(max_length=200)
	code = models.IntegerField(default=0)
	alias = models.CharField(max_length=200)
	token = models.CharField(max_length=200)
	rules = models.TextField()

class Trx(models.Model):
	dr = models.ForeignKey(Coa, related_name="TrxDebit", on_delete=models.DO_NOTHING)
	cr = models.ForeignKey(Coa, related_name="TrxCredit", on_delete=models.DO_NOTHING)
	amt = models.FloatField()
	descr = models.TextField(default="N/A")
	created_at = models.DateTimeField(auto_now=True)

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
	amt = models.FloatField()
	limit = models.FloatField()
	created_at = models.DateTimeField(auto_now=True)