from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for, abort, current_app
)
import urllib.request, urllib.error
import json
import time
import datetime
from . import metrics as M
from . import pings as P

from werkzeug.exceptions import abort

from tracker.db import get_db

bp = Blueprint('pages', __name__)

@bp.before_request
def authenticate():
	if request.args.get('token') != current_app.config["AUTH_TOKEN"]:
		abort(401)


def getTaxonomy(db):
	db_res = db.execute("SELECT id, name, minimum, maximum FROM metrics").fetchall()
	metrics = [M.Metric(m) for m in db_res]
	#[print(m) for m in metrics]

	db_res = db.execute("SELECT t.id AS t_id, t.name AS t_name, c.id AS c_id, c.name AS c_name FROM tags t JOIN categories c ON t.parent == c.id").fetchall()
	categories = M.SQL_to_tags(db_res)
	#[print(m) for m in categories]

	return metrics, categories


@bp.route("/")
def index():
	return redirect(url_for("pages.submit", token=current_app.config["AUTH_TOKEN"]), 303)


@bp.route("/submit", methods=["GET", "POST"])
def submit():
	db = get_db()
	(metrics, categories) = getTaxonomy(db)

	if (request.method == "GET"):
		people = db.execute("SELECT id, name FROM people").fetchall()	

		#metricsJS = '[' + ", ".join([f"{m:js}" for m in metrics]) + ']'
		#categoriesJS = '[' + ", ".join([f"{m:js}" for m in categories]) + ']'
		#taxonomyJS = f"{{\"metrics\": {metricsJS}, \"discrete\": {categoriesJS}}}"
		#print(taxonomyJS)

		lt = time.localtime()
		localtime = f"{lt.tm_hour:02}:{lt.tm_min:02}:{lt.tm_sec:02}"
		localdate = f"{lt.tm_year}-{lt.tm_mon:02}-{lt.tm_mday:02}"
		return render_template("submit.html", **locals())

	person = request.form.get("person", type=int)
	new_tags_res = request.form.getlist("newTags[]")

	res_metrics = [] # tuple of ID and value
	for m in metrics:
		value = request.form.get(f"met_{m.id}")
		if value:
			res_metrics.append((m.id, value))
	
	res_tags = []
	new_tags = [] # tuple of name and parent ID
	for c in range(len(categories)):
		tag = request.form.get(f"tag_{categories[c].id}")
		if tag == "_none":
			continue
		elif tag == "_new":
			new_tags.append((new_tags_res[c], categories[c].id))
		else:
			res_tags.append(tag)
		
	ping_dt_str = request.form.get("datetime")
	print(person, res_metrics, res_tags, new_tags, ping_dt_str)
	if not (person and ping_dt_str):
		abort(400) # client error: bad request

	# 2021-10-12T04:46:53.000Z
	dt_format = "%Y-%m-%dT%H:%M:%S.%fZ"
	print("from request:", ping_dt_str)
	ping_dt = datetime.datetime.strptime(ping_dt_str, dt_format)
	ping_dt = ping_dt.replace(second=0, microsecond=0) # no need
	print(ping_dt) # already in UTC from the browser
	
	# add the ping TODO: parse timestamp
	db.execute("INSERT INTO pings (person, stamp) VALUES (?, ?)", (person, ping_dt))
	db.commit()
	ping_id = db.execute("SELECT id FROM pings ORDER BY id DESC").fetchone()["id"]
	print("new ping added with ID", ping_id)

	# add new tags if needed
	for tag_name, parent_id in new_tags:
		db.execute("INSERT INTO tags (name, parent) VALUES (?, ?)", (tag_name, parent_id))
		db.commit()
		new_tag_id = db.execute("SELECT id FROM tags ORDER BY id DESC").fetchone()["id"]
		res_tags.append(new_tag_id)
		print("new tag added with id", new_tag_id, "and name", tag_name)

	# process glimpses one-by-one
	for val_id, value in res_metrics:
		db.execute("INSERT INTO glimpse_metrics (ping, metric, val) VALUES (?, ?, ?)", (ping_id, val_id, value))
	print("added glimpse metrics")
	
	for tag_id in res_tags:
		db.execute("INSERT INTO glimpse_tags (ping, tag) VALUES (?, ?)", (ping_id, tag_id))
	print("added glimpse tags")

	db.commit()
	return redirect(url_for("pages.submit", token=current_app.config["AUTH_TOKEN"]), 303)


@bp.route("/manage", methods=["GET", "POST"])
def manage():
	db = get_db()
	(metrics, categories) = getTaxonomy(db)

	if (request.method == "GET"):
		people = db.execute("SELECT id, name FROM people").fetchall()

		num_pings = 10

		db_res_categories = db.execute("SELECT gt.ping, p.stamp, per.name AS per_name, c.name AS c_name, t.name AS t_name FROM glimpse_tags gt JOIN pings p ON gt.ping = p.id JOIN people per ON p.person = per.id JOIN tags t ON t.id = gt.tag JOIN categories c on t.parent = c.id ORDER BY gt.ping DESC, c.id ASC").fetchmany(len(categories)*num_pings)

		db_res_metrics = db.execute("SELECT gm.ping, p.stamp, per.name AS per_name, m.name, gm.val FROM glimpse_metrics gm JOIN pings p ON gm.ping = p.id JOIN people per ON p.person = per.id JOIN metrics m ON m.id = gm.metric ORDER BY gm.ping DESC, m.id ASC").fetchmany(len(metrics)*num_pings)

		pings = P.SQL_to_pings(metrics, categories, db_res_metrics, db_res_categories)[:num_pings]
		return render_template("manage.html", **locals())

	table = request.form.get("table")
	id = request.form.get("id")

	if not (table and id and id.isdecimal()):
		print("no table or no valid ID")
		abort(400) # client error: bad request
	
	if table == "pings":
		db.execute("DELETE FROM pings WHERE id = ?", (id,))
		db.commit()
		return redirect(url_for("pages.manage", token=current_app.config["AUTH_TOKEN"]), 303)
	
	action = request.form.get("action")
	if action not in ["create", "update", "delete"]:
		print("invalid action:", action)
		abort(400)

	if table == "categories":
		if action == "delete":
			db.execute("DELETE FROM categories WHERE id = ?", (id,))
		else:
			name = request.form.get("name")
			if not name:
				abort(400)

		if action == "update":
			db.execute("UPDATE categories SET name = ? WHERE id = ?", (name, id))
		elif action == "create":
			if id != "0": # include id requirement for consistency
				abort(400)
			db.execute("INSERT INTO categories (name) VALUES (?)", (name,))
		db.commit()
		return redirect(url_for("pages.manage", token=current_app.config["AUTH_TOKEN"]), 303)

	if table == "tags":
		if action == "delete":
			db.execute("DELETE FROM tags WHERE id = ?", (id,))
		else:
			name = request.form.get("name")
			if not name:
				abort(400)

		if action == "update":
			db.execute("UPDATE tags SET name = ? WHERE id = ?", (name, id))
		elif action == "create":
			db.execute("INSERT INTO tags (name, parent) VALUES (?, ?)", (name, id))
		db.commit()
		return redirect(url_for("pages.manage", token=current_app.config["AUTH_TOKEN"]), 303)

	# if nothing has matched so far, something is wrong
	abort(400)


from collections import namedtuple
import statistics
@bp.route("/stats") # methods=["GET"]
def stats():
	db = get_db()
	(metrics, categories) = getTaxonomy(db)
	people = db.execute("SELECT id, name FROM people").fetchall()

	#samples = db.execute(
	#	"SELECT p.name AS person, c.name AS category, g.name AS genreName, s.stamp AS time FROM samples AS s JOIN categories c ON c.id = s.category JOIN genres g ON g.id = c.genre JOIN people p ON p.id = s.person ORDER BY s.stamp DESC"
	#).fetchall()

	NamedReports   = namedtuple('NamedReports',   'name reports')
	Report         = namedtuple('Report',         'type value') # value can be "Histogram" or "Stats"

	Stats          = namedtuple('Stats',          'name mean stdev')
	
	Histogram      = namedtuple('Histogram',      'name entries')
	HistogramEntry = namedtuple('HistogramEntry', 'bucket portion')

	# future ideas: stats by day of week, histogram by day of week, moving average

	namedReports = []
	for person in people:
		reports = []
		
		# "Stats" type reports
		for metric in metrics:
			values = db.execute("SELECT gm.val FROM glimpse_metrics gm JOIN pings p ON gm.ping = p.id WHERE p.person = ? AND gm.metric = ?", (person["id"], metric.id)).fetchall()
			values = [val["val"] for val in values]
			if len(values) < 2:
				continue
			mean = round(statistics.mean(values), 2)
			stdev = round(statistics.stdev(values), 2)
			reports.append(Report("Stats", Stats(metric.name, mean, stdev)))
		
		# "Histogram" type reports
		for category in categories:
			tags = db.execute("SELECT gt.tag FROM glimpse_tags gt JOIN pings p ON gt.ping = p.id JOIN tags t ON gt.tag = t.id WHERE p.person = ? AND t.parent = ?", (person["id"], category.id)).fetchall()
			tags = [tag["tag"] for tag in tags]
			if not len(tags):
				continue
			buckets = []
			for tag in category.tags:
				prevalence = tags.count(tag.id)/len(tags)
				buckets.append(HistogramEntry(tag.name, round(prevalence*100, 1)))
			reports.append(Report("Histogram", Histogram(category.name, buckets)))

		# put person's name on those reports and add to main list
		namedReports.append(NamedReports(person["name"], reports))
	
	return render_template("stats.html", **locals())
