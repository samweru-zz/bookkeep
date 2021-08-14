import datetime
import random

from django.db.models import Q
from django.db.models.query import QuerySet
from django.db import DatabaseError, transaction
from books.models import Period

import logging

logger = logging.getLogger(__name__)

# Get random date in period
def getRandDate(currPeriod:Period):
	diff = currPeriod.end_date - currPeriod.start_date
	days = random.randrange(diff.days)
	return currPeriod.start_date + datetime.timedelta(days=days)

def new(start:str, end:str):
	try:
		with transaction.atomic():
			start_date = datetime.datetime.strptime(start, "%Y-%m-%d")
			end_date = datetime.datetime.strptime(end, "%Y-%m-%d")
			now = datetime.datetime.now().strftime("%Y-%m-%d")
			today = datetime.datetime.strptime(now, "%Y-%m-%d")

			periods = Period.objects.all()
			for period in periods:
				period.status = "Closed"
				period.save()

			if start_date >= today and end_date > start_date:
				period=Period(start_date=start_date, end_date=end_date)
				period.save()

				return period
			else:
				raise Exception("Dates out of bounds!")
	except DatabaseError as e:
		logger.error(e)
	except ValueError:
		raise ValueError("Incorrect data format, should be YYYY-MM-DD")

	return None

def getCurrent():
	return Period.objects.filter(status="Active").last()

def withQs(qs:QuerySet): 
	currPeriod = getCurrent()
	if currPeriod is not None:
		start_date = currPeriod.start_date.strftime("%Y-%m-%d")
		end_date = currPeriod.end_date.strftime("%Y-%m-%d")
		return qs.filter(Q(created_at__range=[start_date, end_date]))
	return None