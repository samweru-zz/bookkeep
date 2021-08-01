import click
import sys
import os
import django

from books import helper
from django.core.serializers import serialize
import tabulate

 
sys.path.insert(0, "../")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookkeep.settings')
django.setup()

from books.models import *
from books.controllers import accountant as acc

@click.group()
def main():
    pass

@main.command("sch:new")
@click.argument('amt')
@click.argument('descr', required=False)
def new(amt:float, descr:str="N/A"):
	trxNo = acc.getTrxNo("SCH")
	schedule = Schedule(tno=trxNo, amt=amt, descr=descr)	
	click.echo("Trx No.: %s" % trxNo)

@main.command("sch:last")
@click.argument('offset', required=False, default=1)
def sch_last(offset):
	rs = Schedule.objects.all().order_by("-id")[:offset]	
	click.echo(serialize('json', rs, indent=2))

@main.command("trx:last")
@click.argument('offset', required=False, default=1)
def trx_last(offset):
	rs = Trx.objects.all().order_by("-id")[:offset]	
	data = []
	for obj in rs:
		data.append(helper.to_dict(obj))

	click.echo(tabulate.tabulate(data, headers='keys'))

if __name__ == '__main__':
	main()