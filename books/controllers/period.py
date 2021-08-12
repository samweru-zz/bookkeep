import datetime
import random

from django.db.models import Q
from django.db.models.query import QuerySet
from books.models import Period

# Get random date in period
def getRandDate(currPeriod:Period):
	diff = currPeriod.end_date - currPeriod.start_date
	days = random.randrange(diff.days)
	return currPeriod.start_date + datetime.timedelta(days=days)

def new(start:str, end:str):
	try:
		start_date = datetime.datetime.strptime(start, "%Y-%m-%d")
		end_date = datetime.datetime.strptime(end, "%Y-%m-%d")
		today = datetime.datetime.now()

		if start_date > today and end_date > start_date:
			period=Period(start_date=start_date, end_date=end_date)
			period.save()

			return period
	except ValueError:
		raise ValueError("Incorrect data format, should be YYYY-MM-DD")

	return None

def getCurrent():
	return Period.objects.last()

def withQs(qs:QuerySet): 
	currPeriod = getCurrent()
	if currPeriod is not None:
		start_date = currPeriod.start_date.strftime("%Y-%m-%d")
		end_date = currPeriod.end_date.strftime("%Y-%m-%d")
		return qs.filter(Q(created_at__range=[start_date, end_date]))
	return None