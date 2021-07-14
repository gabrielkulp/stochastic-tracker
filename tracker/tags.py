class Tag:
	def __init__(self, db_res):
		self.idx = 0
		self.ID = db_res["id"]
		self.name = db_res["name"]
		self.parent = db_res["parent"]
		self.children = []

	def __str__(self):
		s = f"Tag({self.ID}, {self.name}, "
		s += f"{self.parent.name if self.parent else None}, ["
		s += ', '.join([str(c) for c in self.children])
		s += "])"
		return s
	
	def __format__(self, fmt):
		if fmt == "js":
			# doesn't even include the ID. Client only sees flat indices
			s = f"{{\"idx\": {self.idx}, \"name\": \"{self.name}\", \"parent\": "
			s += f"{self.parent if self.parent else 'null'}, \"children\": ["
			s += ", ".join([str(c) for c in self.children]) + "]}"
			return s
			

def SQL_to_tags(flat_list):
	tree = []
	flat = []
	idx  = 0
	while flat_list:
		new_tag = Tag(flat_list.pop())
		new_tag.idx = idx
		idx += 1
		
		flat.append(new_tag)

		# check if it's a genre
		if new_tag.parent == None:
			tree.append(new_tag)
			continue

		# find who it's a child of
		for t in flat:
			if new_tag.parent == t.ID:
				new_tag.parent = t.idx # convert ID to index
				t.children.append(new_tag.idx)
				break

	return (tree, flat)
