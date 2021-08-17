import click
import sys
import os
import django
import warnings
import json
import logging

from freezegun import freeze_time
from django.core.serializers import serialize
from django.db import DatabaseError, transaction
from django.db import connections as conn
from django.apps import apps

warnings.filterwarnings("ignore")
sys.path.insert(0, "../")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookkeep.settings')
django.setup()

from books.models import *
from books.controllers import period as periodCtr
from books.seeders import sales_order as so
from books.seeders import purchase_order as po

import datetime
import moment

today = datetime.datetime.now()
currPeriod = periodCtr.getCurrent()
if currPeriod is not None:
	today = periodCtr.getRandDate(currPeriod)

logger = logging.getLogger(__name__)

def getModelLs():
	return [

		"TrxType",
		"TrxCfg",
		"Trx",
		"Ledger",
		"Coa",
		"Order",
		"Stock",
		"Catalogue",
		"Period",
		"Schedule"
	]

def getFileBaseLs():
	return [

		"base.catalogue",
		"base.coa",
		"base.trx_cfg",
		"base.trx_type",
	]

def getFileLs():
	return [

		"base.catalogue",
		"base.coa",
		"base.trx_cfg",
		"base.trx_type",
		"alpha.schedule",
		"alpha.ledger",
		"alpha.stocks",
		"alpha.trx"
	]

def seedWithJson(items:list, now:datetime.datetime):
	for item in items:
		module, model = item.get("model").split(".")
		entity = apps.get_model(module, model)()

		fields = item.get("fields")
		props = [f.name for f in entity._meta.fields]		
		fields["created_at"] = now = moment.date(now).add(days=1).date

		for prop in entity._meta.fields:
			if prop.name in fields.keys():
				prop_name = prop.name
				if(prop.related_model is not None):
					prop_name = "%s_id" % prop.name

				setattr(entity, prop_name, fields.get(prop.name))
	
		entity.save()

def seedAll():
	try:
		with transaction.atomic():
			for json_file in getFileLs():
				rand_date = periodCtr.getRandDate(Period.objects.last())
				seedWithJson(json.load(open("fixtures/%s.json" % json_file)), rand_date)
	except DatabaseError as e:
		logger.error(e)


@click.group()
def main():
	pass

@main.command("period:create")
@click.option('--start', '-s', help="yyyy-mm-dd")
@click.option('--end', '-e', help="yyyy-mm-dd")
@click.option('--ignore', '-i',
				is_flag=True,
				default=False,
				help="Creating a fake period by ignoring validation")
def period_create(ignore:bool, start:str=None, end:str=None):
	"""
	Define period start and end date. 
	If not defined will default to today till end year
	"""
	if start is None:
		start = moment.now().format("YYYY-MM-DD")
		# start = moment.now().add(days=1).format("YYYY-MM-DD")

	if end is None:
		end = moment.date("31 dec").format("YYYY-MM-DD")

	currPeriod = periodCtr.new(start, end, ignoreToday=ignore)
	if currPeriod is None:
		click.secho("Couldn't create new period!", fg="red")
	else:
		click.echo("Successully created new period.")
	
@main.command("db:all")
def db_all():
	"""
	Seed database with sample transactions
	"""
	try:
		currPeriod = periodCtr.getCurrent()
		if currPeriod is not None:
			seedAll()

			click.echo("Database seeded successfully!")
		else:
			click.secho("Period must be set first!", fg="red")
	except Exception as e:
		click.secho(e, fg="red")

@main.command("db:base")
def db_base():
	"""
	Seed database without sample transactions
	"""
	try:
		currPeriod = periodCtr.getCurrent()
		if currPeriod is not None:
			for json_file in getFileBaseLs():
				print(json_file)
				rand_date = periodCtr.getRandDate(Period.objects.last())
				seedWithJson(json.load(open("fixtures/%s.json" % json_file)), rand_date)

			click.echo("Database foundation seeded successfully!")
		else:
			click.secho("Period must be set first!", fg="red")
	except Exception as e:
		click.secho(e, fg="red")

@main.command("sales:order")
@freeze_time(today.strftime("%Y-%m-%d %H:%M:%S"))
def sales_order():
	"""
	Seed database with sample sales order transactions
	"""
	currPeriod = periodCtr.getCurrent()
	if currPeriod is None:
		click.secho("Period must be set first!", fg="red")
		exit()

	if so.newSale(item_count=1, created_at=datetime.datetime.now()):
		click.echo("Seeder executed successfully.")
	else:
		click.secho("Failed to execute!", fg="red")

@main.command("purchase:order")
@freeze_time(today.strftime("%Y-%m-%d %H:%M:%S"))
def purchase_order():
	"""
	Seed database with sample purchase order transactions
	"""
	currPeriod = periodCtr.getCurrent()
	if currPeriod is None:
		click.secho("Period must be set first!", fg="red")
		exit()

	if po.newPurchase(cat_count=1, created_at=datetime.datetime.now()):
		click.echo("Seeder executed successfully.")
	else:
		click.secho("Failed to execute!", fg="red")

@main.command("test:freeze")
@freeze_time(moment.date("2 years ago").format("YYYY-MM-DD"))
def test_freeze():
	"""
	test package freeze.gun
	"""
	print(datetime.datetime.now().strftime("%Y-%m-%d"))

if __name__ == '__main__':	
	main()