import click
import sys
import os
import django
import warnings
import json
import logging

from django.core.serializers import serialize
from django.db import DatabaseError, transaction
from django.db import connections as conn
from django.apps import apps

warnings.filterwarnings("ignore")
sys.path.insert(0, "../")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookkeep.settings')
django.setup()

# from freezegun import freeze_time
from books.controllers import period as periodCtr
from books.models import *

import datetime
import moment

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

		"catalogue",
		"coa",
		"trx_cfg",
		"trx_type",
	]

def getFileLs():
	return [

		"catalogue",
		"coa",
		"trx_cfg",
		"trx_type",
		"schedule",
		"ledger",
		"stocks",
		"trx"
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
def period_create(start:str=None, end:str=None):
	"""
	Define period start and end date. 
	If not defined will default to today till end year
	"""
	if start is None:
		start = moment.now().add(days=1).format("YYYY-MM-DD")

	if end is None:
		end = moment.date("31 dec").format("YYYY-MM-DD")

	currPeriod = periodCtr.new(start, end)
	if currPeriod is None:
		click.secho("Couldn't create new period!", fg="red")
	else:
		click.echo("Successully created new period.")
	
@main.command("db:all")
def db_all():
	currPeriod = periodCtr.getCurrent()
	if currPeriod is None:
		click.secho("Period must be set first!", fg="red")
	else:
		seedAll()

@main.command("db:base")
def db_base():
	for file in getFileBaseLs():
		rand_date = periodCtr.getRandDate(Period.objects.last())
		seedWithJson(json.load(open("fixtures/%s.json" % file)), rand_date)

# @main.command("drop:data")
# def drop_data():
# 	with conn["default"].cursor() as cursor:
# 		for model in getModelLs():
# 			sql = "DELETE FROM books_%s" % model.lower()
# 			print(sql)
# 			cursor.execute(sql)		
# 	conn["default"].close()

# @main.command("drop:data")
# def drop_data():
# 	try:
# 		with transaction.atomic():
# 			for model in getModelLs():
# 				oCls = apps.get_model("books", model)
# 				oCls.objects.all().delete()
# 		click.echo("Data successfully dropped!")
# 	except DatabaseError as e:
# 		click.echo("Something went wrong!")

if __name__ == '__main__':	
	main()