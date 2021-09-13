from . import metrics

class Ping:
	def __init__(self, db_res):
		self.id = db_res["ping"]
		self.timestamp = db_res["stamp"]
		self.person = db_res["per_name"]
		# lists of strings for the Manage page
		self.metrics = []
		self.tags = []

def SQL_to_pings(metrics, categories, db_res_metrics, db_res_categories):
	pings = []

	# coalesce tags into list of pings
	for res_cat in db_res_categories:
		if res_cat["ping"] not in [p.id for p in pings]:
			# make new ping
			pings.append(Ping(res_cat))
			pings[-1].tags.append(f"{res_cat['c_name']}→{res_cat['t_name']}")
		else:
			# add to existing ping
			ping = [p for p in pings if p.id == res_cat["ping"]][0]
			ping.tags.append(f"{res_cat['c_name']}→{res_cat['t_name']}")

	# add metrics to that list
	for res_met in db_res_metrics:
		if res_met["ping"] not in [p.id for p in pings]:
			# make new ping
			pings.append(Ping(res_met))
			pings[-1].metrics.append(f"{res_met['name']}: {res_met['val']}")
		else:
			# add to existing ping
			ping = [p for p in pings if p.id == res_met["ping"]][0]
			ping.metrics.append(f"{res_met['name']}: {res_met['val']}")
	
	return sorted(pings, key=lambda ping: ping.id, reverse=True)
