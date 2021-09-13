class Metric:
	def __init__(self, db_res):
		self.id = db_res["id"]
		self.name = db_res["name"]
		self.min = db_res["minimum"]
		self.max = db_res["maximum"]
	
	def __str__(self):
		s = f"Metric({self.id}, {self.name}, "
		s += f"({self.min})->({self.max}))"
		return s
	
	def __format__(self, fmt):
		if fmt == "js":
			s = f"{{\"id\": {self.id}, \"name\": \"{self.name}\", "
			s += f"\"min\": {self.min}, \"max\": {self.max}}}"
			return s
		else:
			return str(self)

class Category:
	def __init__(self, db_res):
		self.id = db_res["c_id"]
		self.name = db_res["c_name"]
		self.tags = []
	
	def __str__(self):
		s = f"Category({self.id}, {self.name}, ["
		s += ', '.join([str(t) for t in self.tags])
		s += "])"
		return s
	
	def __format__(self, fmt):
		if fmt == "js":
			s = f"{{\"id\": {self.id}, \"name\": \"{self.name}\", \"tags\": ["
			s += ", ".join([f"{t:js}" for t in self.tags])
			s += "]}"
			return s
		else:
			return str(self)


class Tag:
	def __init__(self, db_res):
		self.id = db_res["t_id"]
		self.name = db_res["t_name"]

	def __str__(self):
		return f"Tag({self.id}, {self.name})"

	def __format__(self, fmt):
		if fmt == "js":
			# doesn't even include the ID. Client only sees flat indices
			s = f"{{\"id\": {self.id}, \"name\": \"{self.name}\"}}"
			return s
		else:
			return str(self)


def SQL_to_tags(db_res):
	categories = []
	for tag in db_res:
		if tag["c_id"] not in [c.id for c in categories]:
			# create new category
			categories.append(Category(tag))
			categories[-1].tags.append(Tag(tag))
		else:
			# add to existing category
			category = [c for c in categories if c.id == tag["c_id"]][0]
			category.tags.append(Tag(tag))

	return categories
