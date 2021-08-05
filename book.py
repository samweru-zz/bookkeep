import click
import sys
import os
import django
import warnings
import tabulate
import datetime

# from freezegun import freeze_time
# freezer = freeze_time("2012-01-14")
# freezer.start()

from django.core.serializers import serialize
from django.db import DatabaseError, transaction

warnings.filterwarnings("ignore")
sys.path.insert(0, "../")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookkeep.settings')
django.setup()

from books import helper
from books.models import *
from books.controllers import accountant as acc
from books.controllers import purchase as pur
from books.controllers.inventory import Order as InvOrder

@click.group()
# @freeze_time("1955-11-12")
def main():
    pass

@main.command("sch:new")
@click.argument('descr')
@click.argument('amt', required=False, default=0.00)
def new(descr:str, amt:float):
	trxNo = acc.getTrxNo("SCH")
	sch = Schedule(tno=trxNo, amt=amt, descr=descr)
	sch.save()
	click.echo("Trx No.: %s | Id: %d | Amount: %d" % (trxNo, sch.id, sch.amt))

@main.command("sch:last")
@click.argument('offset', required=False, default=1)
def sch_last(offset):
	rs = Schedule.objects.all().order_by("-id")[:offset]
	if rs.count()>0:
		data = helper.to_rslist(rs)
		click.echo(tabulate.tabulate(data, headers='keys'))
	else:
		click.echo("Couldn't find anything!")

@main.command("sch:push")
@click.argument('id')
@click.option("--ttype", type=click.Choice(['lpo', 'none'], case_sensitive=False), required=True)
@click.option("--descr", default="N/A")
def sch_push(id:int, descr:str, ttype:str):
	try:
		with transaction.atomic():
			sch = Schedule.objects.get(id=id)
			sch.status="Final"
			sch.save()

			trxNo = sch.tno
			if(ttype == "lpo"):
				trxNo = acc.withTrxNo("PUR", sch.tno)

			order = InvOrder.findByTrxNo(trxNo)
			trx = pur.order(order, descr)
	except DatabaseError as e:
		logger.error(e)

	click.echo("Purchase Trx | No.: %s created successfully!" % trx.tno)

@main.command("trx:last")
@click.argument('offset', required=False, default=1)
def trx_last(offset):
	rs = Trx.objects.all().order_by("-id")[:offset]	
	data = helper.to_rslist(rs)
	click.echo(tabulate.tabulate(data, headers='keys'))

@main.command("cat:new")
@click.argument('name')
@click.argument('price')
@click.argument('descr', required=False, default="N/A")
# @freeze_time("1955-11-12")
def cat_new(name:str, price:float, descr:str):
	cat = Catalogue(name=name, price=price, descr=descr, status="Active")
	cat.save()
	click.echo("Id: %d | Name: %s | Amount: %s" % (cat.id, cat.name, cat.price))

@main.command("cat:last")
@click.argument('offset', required=False, default=1)
def cat_last(offset):
	rs = Catalogue.objects.all().order_by("-id")[:offset]	
	data = helper.to_rslist(rs)
	click.echo(tabulate.tabulate(data, headers='keys'))

@main.command("cat:filter")
@click.argument('name')
def cat_filter(name):
	rs = Catalogue.objects.filter(name__icontains=name)
	if rs.count()>0:
		data = helper.to_rslist(rs)
		click.echo(tabulate.tabulate(data, headers='keys'))
	else:
		click.echo("Couldn't find anything!")

@main.command("lpo:add")
@click.argument('sch_id')
@click.argument('cat_id')
@click.argument('units')
@click.argument('unit_cost')
def lpo_add(sch_id:int, cat_id:int, units:int, unit_cost:float):
	"""Add a number of units of a categorized item to a local purchase order"""
	try:
		with transaction.atomic():
			sch = Schedule.objects.get(id=sch_id)
			tt_amt = float(unit_cost) * int(units)
			sch.amt = sch.amt + tt_amt
			sch.save()

			cat = Catalogue.objects.get(id=cat_id)

			code = acc.getCode()
			ptrxNo = acc.withTrxNo("PUR", sch.tno)
			order = Stock(tno=ptrxNo, 
						cat=cat, 
						code=code, 
						unit_total=units, 
						unit_cost=unit_cost, 
						status="Order:Pending")
			order.save()
	except Exception as e:
		click.echo("Purcase Order: Couldn't add item!")
	except DatabaseError as e:
		click.echo("Something went wrong!")


@main.command("stock:filter")
@click.argument('name')
def stock_filter(name):
	rs = Stock.objects.filter(cat__name__icontains=name)
	data = []
	if rs.count()>0:
		for row in rs:
			data.append({

				"id":row.id,
				"tno":row.tno,
				"name":row.cat.name,
				"code":row.code,
				"unit_bal":row.unit_bal,
				"unit_total":row.unit_total,
				"unit_cost":row.unit_cost,
				"status":row.status,
				"created_at":row.created_at.strftime("%A %d. %B %Y")
			})
		click.echo(tabulate.tabulate(data, headers='keys'))
	else:
		click.echo("Couldn't find anything!")

@main.command("stock:last")
@click.argument('offset', required=False, default=1)
def stock_last(offset):
	rs = Stock.objects.all().order_by("-id")[:offset]
	data = []
	for row in rs:
		data.append({

			"id": row.id,
			"trx_no":row.tno,
			"name": row.cat.name,
			"balance": row.unit_bal,
			"unit_cost": float(row.unit_cost),
			"total_units":row.unit_total,
			"status":row.status,
			"created_at":row.created_at.strftime("%A %d. %B %Y")
		})

	click.echo(tabulate.tabulate(data, headers='keys'))

@main.command("entry:last")
@click.argument('offset', required=False, default=1)
def entry_last(offset):
	rs = Ledger.objects.all().order_by("-id")[:offset]	
	data = []
	for row in rs:
		data.append({

			"id":row.id,
			"trx_no":row.tno,
			"trx_type":"dr:%s|cr:%s" % (row.dr.name, row.cr.name),
			"amt":row.amt,
			"created_at":row.created_at.strftime("%A %d. %B %Y")
		})

	click.echo(tabulate.tabulate(data, headers='keys'))

# @main.command("test:test")
# @freeze_time("1955-11-12")
# def test():
	# with freeze_time("1955-11-12"):
	# print(datetime.now().strftime("%Y-%m-%d"))

if __name__ == '__main__':	
	main()

# freezer.stop()