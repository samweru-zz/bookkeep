import click
import sys
import os
import django
import warnings
import tabulate
import datetime
import re
import logging

from django.core.serializers import serialize
from django.db import DatabaseError, transaction
from django.db.models import Q

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
from books.controllers import inventory as inv
from books.controllers.inventory import Requisition as InvReq
from books.controllers import period as periodCtr
from pick import pick

logger = logging.getLogger(__name__)

def get_label(option): return option.get('label')

@click.group()
def main():
    pass

@main.command("sch:new")
@click.argument('descr')
@click.argument('amt', required=False, default=0.00)
@click.option("--ttype", type=click.Choice(['lpo', 'sale', 'saleret'], case_sensitive=False), 
							required=True)
def sch_new(descr:str, amt:float, ttype:str):
	"""
	Create new schedule
	"""
	trxNo = None
	if ttype == "lpo":
		trxNo = acc.getTrxNo("PUR")
	elif ttype == "sale":
		trxNo = acc.getTrxNo("INV")
	elif ttype == "saleret":
		oTrxNo = click.prompt('Trx No:')
		trx = Trx.objects.filter(tno=oTrxNo).first()
		if trx is not None:
			trxNo = acc.withTrxNo("SRT", oTrxNo)

	if trxNo is not None:
		sch = Schedule(tno=trxNo, amt=amt, descr=descr)
		sch.save()
		click.echo("Trx No.: %s | Id: %d | Amt: %s" % 
			(trxNo, sch.id, "Kshs. {:,.2f}".format(sch.amt)))
	else:
		click.secho("Couldn't generate a valid TrxNo!", fg="red")

@main.command("sch:last")
@click.argument('offset', required=False, default=1)
def sch_last(offset):
	"""
	View X number of last schedules
	"""
	rs = periodCtr.withQs(Schedule.objects.all().order_by("-id"))

	rs = rs[:offset]
	if rs.count()>0:
		data = helper.to_rslist(rs)
		for item in data:
			item["amt"] = "Kshs. {:,.2f}".format(item["amt"])

		click.echo(tabulate.tabulate(data, headers='keys'))
	else:
		click.echo("Couldn't find anything!")

@main.command("sch:push")
@click.argument('id')
@click.option("--descr", default="N/A")
def sch_push(id:int, descr:str):
	"""
	Push schedule into transaction
	"""
	try:
		sch = Schedule.objects.get(id=id)
		if sch.status != "Final":
			with transaction.atomic():
				sch.status="Final"
				sch.save()

				trxNoPrefix = sch.tno[:3]
				if trxNoPrefix == "PUR":
					req = InvReq.findByTrxNo(sch.tno)
					trx = pur.order(req, descr)
				elif trxNoPrefix == "INV":
					salesOrder = cust.Order.findByTrxNo(sch.tno)
					trx = sale.invoice(salesOrder, descr)
				elif trxNoPrefix == "SRT":
					salesOrder = cust.Order.findByTrxNo(sch.tno)
					trx = sale.returns(salesOrder)
			click.echo("Schedule pushed successfully.")
		else:
			click.echo("Schedule already pushed!")
	except DatabaseError as e:
		click.secho(e, fg="red")

@main.command("trx:last")
@click.argument('offset', required=False, default=1)
def trx_last(offset):
	"""
	View X number of last transactions
	"""
	rs = periodCtr.withQs(Trx.objects.all().order_by("-id"))

	data = helper.to_rslist(rs[:offset])
	for item in data:
		item["qamt"] = "Kshs. {:,.2f}".format(item['qamt'])
		item["bal"] = "Kshs. {:,.2f}".format(item['bal'])

	click.echo(tabulate.tabulate(data, headers='keys'))

@main.command("cat:new")
@click.argument('name')
@click.argument('price')
@click.argument('descr', required=False, default="N/A")
def cat_new(name:str, price:float, descr:str):
	"""
	Create new catalogue item
	"""
	cat = Catalogue(name=name, price=price, descr=descr, status="Active")
	cat.save()
	click.echo("Id: %d | Name: %s | Amt: %s" % (cat.id, cat.name, "Kshs. {:,.2f}".format(cat.price)))

@main.command("cat:last")
@click.argument('offset', required=False, default=1)
def cat_last(offset):
	"""
	View X number of last catalogues
	"""
	rs = Catalogue.objects.all().order_by("-id")[:offset]

	data = helper.to_rslist(rs)
	for item in data:
		item["price"] = "Kshs. {:,.2f}".format(item["price"])

	click.echo(tabulate.tabulate(data, headers='keys'))

@main.command("cat:filter")
@click.argument('name')
def cat_filter(name):
	"""
	Catalogue filter items
	"""
	rs = Catalogue.objects.filter(name__icontains=name)
	if rs.count()>0:
		data = helper.to_rslist(rs)
		click.echo(tabulate.tabulate(data, headers='keys'))
	else:
		click.echo("Couldn't find anything!")

@main.command("lpo:add")
@click.argument('sch_id')
@click.argument('units')
@click.argument('unit_cost')
def lpo_add(sch_id:int, units:int, unit_cost:float):
	"""
	Add a number of units of a categorized item to a local purchase order
	"""
	try:
		with transaction.atomic():
			sch = Schedule.objects.get(id=sch_id)
			if sch.status == "Pending":
				tt_amt = float(unit_cost) * int(units)
				sch.amt = sch.amt + tt_amt
				sch.save()

				options = []
				cats = Catalogue.objects.filter(status="Active")
				for cat in cats:
					options.append({'label':cat.name, 'id':cat.id})

				title = 'Please choose an item: '
				selected = pick(options, title, indicator='*', options_map_func=get_label)
				cat_id = selected[0]["id"]

				cat = Catalogue.objects.get(id=cat_id)
				if cat.status == "Active":
					code = acc.getCode()
					ptrxNo = acc.withTrxNo("PUR", sch.tno)
					order = Stock(tno=ptrxNo, 
				 				cat=cat, 
								code=code, 
								unit_bal=units,
								unit_total=units, 
								unit_cost=unit_cost, 
								status="Order:Pending")
					order.save()

					click.echo("Batch Code: %s" % code)
				else:
					click.secho("Catalogue item status must be [Active]!", fg="red")
			else:
				click.secho("Schedule status must be [Pending]!", fg="red")
	except Exception as e:
		# logger.error(e)
		click.echo("Purcase Order: Couldn't add item!")
	except DatabaseError as e:
		click.echo("Something went wrong!")

@main.command("lpo:pay")
@click.argument('trx_id')
@click.argument('amt', required=False)
def lpo_pay(trx_id:int, amt:float=None):
	"""
	Make payment for purchase order
	"""
	try:
		with transaction.atomic():
			trx = Trx.objects.get(id=trx_id)
			if trx.status != "Final":
				if amt is None:
					amt = trx.bal

				if pur.pay(trxNo=trx.tno, amt=amt):
					stocks = Stock.objects.filter(tno=trx.tno)
					for stock in stocks:
						stock.status = "Pending"
						stock.save()

					click.echo("Purchase payment successful!")
				else:
					click.secho("Purchase payment failed!", fg="red")
			else:
				click.echo("Trx already finalized!")
	except DatabaseError as e:
		click.secho(e, fg="red")

@main.command("stock:filter")
@click.argument('name')
def stock_filter(name):
	"""
	Filter stock items
	"""
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
				"unit_cost":"Kshs. {:,.2f}".format(row.unit_cost),
				"status":row.status,
				"created_at":row.created_at.strftime("%A %d. %B %Y")
			})
		click.echo(tabulate.tabulate(data, headers='keys'))
	else:
		click.echo("Couldn't find anything!")

@main.command("stock:last")
@click.argument('offset', required=False, default=1)
def stock_last(offset):
	"""
	View X number of stock items
	"""
	rs = Stock.objects.all().order_by("-id")[:offset]
	data = []
	for row in rs:
		data.append({

			"id": row.id,
			"trx_no":row.tno,
			"name": row.cat.name,
			"units_balance": row.unit_bal,
			"total_units":row.unit_total,
			"unit_cost": "Kshs. {:,.2f}".format(row.unit_cost),
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
	"""
	View X number of last transaction entries
	"""
	rs = periodCtr.withQs(Ledger.objects.all().order_by("-id"))
	data = []
	for row in rs[:offset]:
		data.append({

			"id":row.id,
			"trx_no":row.tno,
			"trx_type":"dr:%s|cr:%s" % (row.dr.name, row.cr.name),
			"amt":"Kshs. {:,.2f}".format(row.amt),
			"created_at":row.created_at.strftime("%A %d. %B %Y")
		})

	click.echo(tabulate.tabulate(data, headers='keys'))

@main.command("sale:disc")
@click.argument('trx_id')
@click.argument('amt')
def sale_discount(trx_id:int, amt:int):
	"""
	Apply sales discount
	"""
	click.echo("To be implemented!")

@main.command("sale:rec")
@click.argument('trx_id')
@click.argument('amt', required=False)
def sale_receipt(trx_id:int, amt:int=None):
	"""
	Receive payment for sales order
	"""
	trx = Trx.objects.get(id=id)
	if trx.status != "Final":
		if sale.receipt(trxNo=trx.tno, amt=amt):
			click.echo("Sales transaction successfully saved.")
		else:
			click.echo("Sales transaction failed!")
	else:
		click.echo("Transaction already finalized!")

@main.command("trx:id")
@click.argument('tid')
def trx_id(tid:str):
	"""
	Find transaction by ID or TRXNO. Note: TRXNO is still used in the schedule.
	"""
	trx = None
	if tid.isnumeric():
		trx = Trx.objects.filter(id=tid).first()
	elif tid.isalnum():
		trx = Trx.objects.filter(tno__icontains=tid).first()

	if trx is None:
		click.secho("Couldn't find transaction!", fg="red")
	else:
		click.echo("\nId: %d | Trx No: %s | Amt: %s | Bal: %s | Status: %s \n" % 
					(trx.id, trx.tno, 
						"Kshs. {:,.2f}".format(trx.qamt),
						"Kshs. {:,.2f}".format(trx.bal), trx.status))

		rs = Ledger.objects.filter(tno__icontains=trx.tno[3:])

		data = []
		for row in rs:
			data.append({

				"id":row.id,
				"trx_no":row.tno,
				"trx_type":"dr:%s|cr:%s" % (row.dr.name, row.cr.name),
				"amt":"Kshs. {:,.2f}".format(row.amt),
				"created_at":row.created_at.strftime("%A %d. %B %Y")
			})

		click.echo(tabulate.tabulate(data, headers='keys'))


@main.command("sale:ret")
@click.argument('ord_id')
@click.argument('units')
@click.option("--descr", default="N/A")
def sale_return(ord_id:int, units:int, descr:str):
	"""
	Sales return units per order
	"""
	try:
		with transaction.atomic():
			order = Order.objects.get(id=ord_id)
			trx = Trx.objects.filter(tno=order.tno).first()

			if int(units) <= int(order.units): 
				tt_cost = int(units) * order.item.unit_cost
				tt_price = int(units) * order.item.cat.price

			trxNo = acc.withTrxNo("SRT", order.tno)
			sch = Schedule.objects.filter(tno=trxNo).first()
			if sch is None:
				sch = Schedule(tno=trxNo, descr=descr)
				sch.amt = 0 

			sch.amt = sch.amt + tt_cost

			Order(tno=trxNo, item=order.item, units=units, status="Returned").save()
			
			sch.save()

			click.echo("Sales order reversed successfully.")
	except DatabaseError as e:
		logger.error(e)

@main.command("sale:add")
def sale_add():
	"""
	Add to sales order.
	"""
	sch_id = click.prompt('Schedule Id', type=int)
	units = click.prompt('Units', type=int)

	options = []
	cats = Catalogue.objects.filter(status="Active")
	for cat in cats:
		options.append({'label':cat.name, 'id':cat.id})

	title = 'Please choose an item: '
	selected = pick(options, title, indicator='*', options_map_func=get_label)
	cat_id = selected[0]["id"]
 
	try:
		with transaction.atomic():
			sch=Schedule.objects.get(id=sch_id)
			cat=Catalogue.objects.get(id=cat_id)

			custOrder = cust.Order.findByTrxNo(sch.tno)
			isOrderEmpty = custOrder.isEmpty()
			custOrder.addItem(cat=cat, units=int(units))

			if isOrderEmpty:	
				custOrder.saveWithTrxNo(sch.tno)
			else:
				custOrder.save()

			sch.amt = custOrder.getTotalPrice()
			sch.save()

			click.echo("Sales Order: Item added successfully.")
	except Exception as e:
		logger.error(e)
	except DatabaseError as e:
		click.echo("Something went wrong!")

@main.command("period:last")
@click.argument('offset', required=False, default=1)
def period_last(offset):
	"""
	Last period should be the active period
	otherwise someone may be viewing records from another period
	"""
	rs = Period.objects.all().order_by("-id")[:offset]	
	data = []
	for row in rs:
		data.append({

			"id":row.id,
			"start":row.start_date.strftime("%A %d. %B %Y"),
			"end":row.end_date.strftime("%A %d. %B %Y"),
			"status": row.status
		})

	if len(data) == 0:
		click.secho("There are no periods!", fg="red")
	else:
		click.echo(tabulate.tabulate(data, headers='keys'))

@main.command("order:last")
@click.argument('offset', required=False, default=1)
def order_last(offset):
	"""
	View X number of last order items
	"""
	rs = periodCtr.withQs(Order.objects.all().order_by("-id"))
	data = []
	for row in rs[:offset]:
		data.append({

			"id":row.id,
			"trx_no":row.tno,
			"catalogue":row.item.cat.name,
			"units":row.units,
			"status":row.status,
			"created_at":row.created_at.strftime("%A %d. %B %Y")
		})

	click.echo(tabulate.tabulate(data, headers='keys'))

@main.command("order:rev")
@click.argument('id')
def order_revert(id:int):
	"""
	Revert order only by schedule
	"""
	try:
		with transaction.atomic():
			order = Order.objects.get(id=id)
			schedule = Schedule.objects.get(tno=order.tno)
			if order != None and schedule != None:
				if schedule.status == "Pending" and order.status == "Pending":
					inv.revert(order)
					tt_rev_price = order.units * order.item.cat.price
					schedule.amt = schedule.amt - tt_rev_price
					schedule.save()

					click.echo("Order successfully reverted.")
				else:
					click.secho("Schedule is closed or order is finalized!", fg="red")
			else:
				click.secho("Order may not exist!", fg="red")
	except DatabaseError as e:
		logger.error(e)
	except Exception as e:
		# logger.error(e)
		click.echo("Something went wrong!")

@main.command("order:filter")
@click.argument('filtr')
def order_filter(filtr:str):
	"""
	Filter ordered items either by trx_no (transaction number) or catalogue item name
	"""
	orders = Order.objects.filter(Q(tno__icontains=filtr)|Q(item__cat__name__icontains=filtr))
	rs = periodCtr.withQs(orders.order_by("-id"))
	data = []
	for row in rs:
		data.append({

			"id":row.id,
			"trx_no":row.tno,
			"catalogue":row.item.cat.name,
			"units":row.units,
			"status":row.status,
			"created_at":row.created_at.strftime("%A %d. %B %Y")
		})

	click.echo(tabulate.tabulate(data, headers='keys'))

if __name__ == '__main__':	
	main()