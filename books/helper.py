import datetime

def to_dict(model):
	data = {}
	for field in model._meta.fields:
		obj = getattr(model, field.name)
		if isinstance(obj, datetime.datetime):
			data[field.name] = obj.strftime("%A %d. %B %Y")
		else:
			data[field.name] = obj
	return data