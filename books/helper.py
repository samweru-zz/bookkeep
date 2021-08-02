import datetime

from books import helper

def to_dict(model):
	data = {}
	for field in model._meta.fields:
		obj = getattr(model, field.name)
		if isinstance(obj, datetime.datetime):
			data[field.name] = obj.strftime("%A %d. %B %Y")
		else:
			data[field.name] = obj
	return data


def rs_to_dict(rs):
	data = []
	for obj in rs:
		data.append(helper.to_dict(obj))

	return data