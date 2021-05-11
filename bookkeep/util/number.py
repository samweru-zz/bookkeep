import numbers

class Number:
	def __init__(self, num):
		self.num = num

	def alloc(self, *args):
		args = list(args)
		if(all(isinstance(arg, (int, float)) for arg in args)):
			allocs = []
			if(sum(args) <= 1):
				if(sum(args) < 1):
					args.append(1 - sum(args))

				for arg in args:
					if(isinstance(arg, numbers.Number)):
						allocs.append(arg * self.num)
			return allocs
		return None
