import click
import sys
import os
import django
import warnings
import json
import datetime

from django.core.serializers import serialize
from django.db import DatabaseError, transaction
from django.apps import apps

warnings.filterwarnings("ignore")
sys.path.insert(0, "../")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookkeep.settings')
django.setup()

from freezegun import freeze_time
from books.controllers import period as periodCtr
from books.models import *

def seedAll():
	for json_file in os.listdir("fixtures"):
		items = json.load(open("fixtures/%s" % json_file))
		for item in items:
			module, model = item.get("model").split(".")
			entity = apps.get_model(module, model)()

			fields = item.get("fields")
			props = [f.name for f in entity._meta.fields]
			if "created_at" in props:
				fields["created_at"] = datetime.datetime.now().strftime("%Y-%m-%d")

			for prop in entity._meta.fields:
				if prop.name in fields.keys():
					prop_name = prop.name
					if(prop.related_model is not None):
						prop_name = "%s_id" % prop.name
					
					setattr(entity, prop_name, fields.get(prop.name))
		
			entity.save()

@click.group()
def main():
	pass

@main.command("seed:period")
@click.option('--start', '-s', help="yyyy-mm-dd", required=True)
@click.option('--end', '-e', help="yyyy-mm-dd", required=True)
def seed_period(start:str, end:str):
	currPeriod = periodCtr.new(start, end)
	if currPeriod is None:
		click.secho("Couldn't created new period!", fg="red")
	else:
		click.echo("Successully created new period.")
	

@main.command("seed:all")
@click.option('--date', '-d', help="yyyy-mm-dd")
def seed_all(date:str=None):
	if date is None:
		seedAll()
	else:
		with freeze_time(datetime.datetime.strptime(date, "%Y-%m-%d")):
			seedAll()

if __name__ == '__main__':	
	main()