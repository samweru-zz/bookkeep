from books.models import Period

def getCurrent():
	return Period.objects.last()