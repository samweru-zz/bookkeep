class Ruler:
	def __init__(self, rule: str):
		self.rule = rule

	def parse(self, rule: str):
		return [{item.split(":")[0]:item.split(":")[-1]} for item in [rules for rules in rule.split("|")]]

	def verify(self, cond: str):
		for item in [rules for rules in self.rule.split("|")]:
			
				return True
		return False

	def get(self, key):
		for item in [rules for rules in self.rule.split("|")]:
			if item.startswith("has:"+key) and item.__contains__("@"):
				return item.split("@")[-1]
		return None 
