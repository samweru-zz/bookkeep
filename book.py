import click
import sys
import os
import django
import warnings
import tabulate
import datetime
import re

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
from books.controllers import customer as cust
from books.controllers import sale
from books.controllers.inventory import Requisition as InvReq

@click.group()
# @freeze_time("1955-11-12")
def main():
    pass

@main.command("sch:new")
@click.argument('descr')
@click.argument('amt', required=False, default=0.00)
def sch_new(descr:str, amt:float):
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
@click.option("--ttype", type=click.Choice(['lpo', 'sale', 'none'], case_sensitive=False), 
							required=True)
@click.option("--descr", default="N/A")
def sch_push(id:int, descr:str, ttype:str):
	try:
		with transaction.atomic():
			sch = Schedule.objects.get(id=id)
			sch.status="Final"
			sch.save()

			trxNo = sch.tno
			if ttype == "lpo":
				trxNo = acc.withTrxNo("PUR", sch.tno)
				req = InvReq.findByTrxNo(trxNo)
				trx = pur.order(req, descr)
			elif ttype == "sale":
				trxNo = acc.withTrxNo("SAL", sch.tno)
				salesOrder = cust.Order.findByTrxNo(trxNo)
				sale.invoice(salesOrder, descr)
	except DatabaseError as e:
		logger.error(e)

	click.echo("Schedule | Trx No.: %s created successfully!" % trx.tno)

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

@main.command("entry:rev")
@click.argument('id')
@click.argument('amt', required=False, default=None)
def entry_rev(id:int, amt:float):
	"""
	Reverse a transaction entry
	"""
	oEntry = Ledger.objects.get(id=id)
	trx = Trx.objects.filter(tno__icontains=oEntry.tno[3:])[0]

	status = None
	if amt is None:
		amt = oEntry.amt

	if amt <= oEntry.amt and amt <= trx.bal:
		try:
			with transaction.atomic():
				nEntry = acc.reverse(entry=oEntry, amt=amt)
				nEntry.save()

				if status is not None:
					oEntry.save()
		except DatabaseError as e:
			logger.error(e)

		click.echo("Rev.Id: %d | Rev.TrxNo: %s" % (nEntry.id, nEntry.tno))
	else:
		click.echo("Failed to reverse!")
 
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

@main.command("sale:disc")
@click.argument('trx_id')
@click.argument('amount')
def sale_disc(trx_id:int, amount:int):
	"""Apply sales discount"""
	click.echo("To be implemented!")

@main.command("sale:add")
def sale_add():
	"""Add to sales order"""
	sch_id = click.prompt('Schedule Id', type=int)
	cat_id = click.prompt('Catalogue Id', type=int)
	units = click.prompt('Number of Units', type=int)
 
	try:
		with transaction.atomic():
			sch=Schedule.objects.get(id=sch_id)
			cat=Catalogue.objects.get(id=cat_id)

			trxNo = acc.withTrxNo("SAL", sch.tno)

			custOrder = cust.Order.findByTrxNo(trxNo)
			isOrderEmpty = custOrder.isEmpty()
			custOrder.addItem(cat=cat, units=int(units))

			if isOrderEmpty:	
				custOrder.saveWithTrxNo(trxNo)
			else:
				custOrder.save()

			sch.amt = custOrder.getTotalPrice()
			sch.save()

		click.echo("Sales Order: Item added successfully.")
	except Exception as e:
		click.echo("Sales Order: Couldn't add item!")
	except DatabaseError as e:
		click.echo("Something went wrong!")

@main.command("order:last")
@click.argument('offset', required=False, default=1)
def order_last(offset):
	rs = Order.objects.all().order_by("-id")[:offset]	
	data = []
	for row in rs:
		data.append({

			"id":row.id,
			"trx_no":row.tno,
			"catalogue":row.item.cat.name,
			"status":row.status,
			"created_at":row.created_at.strftime("%A %d. %B %Y")
		})

	click.echo(tabulate.tabulate(data, headers='keys'))

if __name__ == '__main__':	
	main()