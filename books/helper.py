import datetime

from books import helper

def to_dict(model, exclude:list=[]):
	data = {}
	for field in model._meta.fields:
		if field.name not in exclude:
			obj = getattr(model, field.name)
			if isinstance(obj, datetime.datetime):
				data[field.name] = obj.strftime("%A %d. %B %Y")
			else:
				data[field.name] = obj
	return data


def to_rslist(rs, exclude:list=[]):
	data = []
	for obj in rs:
		data.append(helper.to_dict(obj, exclude))

	return data