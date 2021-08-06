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
from freezegun import freeze_time

@click.group()
def main():
	warnings.filterwarnings("ignore")
	sys.path.insert(0, "../")
	os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookkeep.settings')
	django.setup()

@main.command("seed:all")
@freeze_time("2012-01-14")
def all():
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

if __name__ == '__main__':	
	main()