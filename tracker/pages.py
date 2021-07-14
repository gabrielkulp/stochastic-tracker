from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for, abort
)
import urllib.request, urllib.error
import json
import time
from . import tags as T

from werkzeug.exceptions import abort

from tracker.db import get_db

bp = Blueprint('pages', __name__)


@bp.route("/")
def index():
	return redirect(url_for("pages.submit"), 303)

@bp.route("/submit", methods=["GET", "POST"])
def submit():
	db = get_db()
	if (request.method == "GET"):
		people = db.execute("SELECT id, name FROM people").fetchall()
		db_res = db.execute("SELECT id, name, parent FROM tags ORDER BY id DESC").fetchall()
		(tags_tree, tags_flat) = T.SQL_to_tags(db_res)
		tagsJS = '[' + ", ".join([f"{g:js}" for g in tags_flat]) + ']'
		lt = time.localtime()
		localtime = f"{lt.tm_hour:02}:{lt.tm_min:02}"
		# cspell: ignore mday
		localdate = f"{lt.tm_year}-{lt.tm_mon:02}-{lt.tm_mday:02}"
		return render_template("submit.html", **locals())

	person = request.form.get("person", type=int)
	glimpses = request.form.getlist("glimpses[]")
	new_tags = request.form.getlist("newTags[]")
	ping_date = request.form.get("date")
	ping_time = request.form.get("time")
	print(person, glimpses, new_tags, ping_date, ping_time)
	if not (person and glimpses and new_tags and ping_date and ping_time):
		abort(400) # client error: bad request

	db_res = db.execute("SELECT id, name, parent FROM tags ORDER BY id DESC").fetchall()
	(tags_tree, tags_flat) = T.SQL_to_tags(db_res)
	
	# add the ping TODO: parse timestamp
	db.execute("INSERT INTO pings (person) VALUES (?)", (person,))
	db.commit()
	ping_id = db.execute("SELECT id FROM pings ORDER BY id DESC").fetchone()["id"]
	print("new ping added with ID", ping_id)

	# process glimpses one-by-one
	for (glimpse, new_tag) in zip(glimpses, new_tags):
		# cspell: ignore isdecimal
		if glimpse.isdecimal():
			tag_id = tags_flat[int(glimpse)].ID
			db.execute("INSERT INTO glimpses (ping, tag) VALUES (?, ?)", (ping_id, tag_id))
		elif glimpse[3:].isdecimal():
			# if it's not decimal, it's probably a new tag
			parent_id = tags_flat[int(glimpse[3:])].ID
			if new_tag:
				db.execute("INSERT INTO tags (name, parent) VALUES (?, ?)", (new_tag, parent_id))
			else:
				# no empty tag names!
				# TODO: rollback ping and other glimpses?
				abort(400)
			
			# now we need the ID of that new tag so we can insert a glimpse with it
			db.commit()
			tag_id = db.execute("SELECT id FROM tags ORDER BY id DESC").fetchone()["id"]
			db.execute("INSERT INTO glimpses (ping, tag) VALUES (?, ?)", (ping_id, tag_id))
		else:
			# invalid glimpse ID
			# TODO: rollback ping and other glimpses?
			abort(400)

	db.commit()
	return redirect(url_for("pages.submit"), 303)


@bp.route("/manage", methods=["GET", "POST"])
def manage():
	db = get_db()
	if (request.method == "GET"):
		people = db.execute("SELECT id, name FROM people").fetchall()
		db_res = db.execute("SELECT id, name, parent FROM tags ORDER BY id DESC").fetchall()
		(tags_tree, tags_flat) = T.SQL_to_tags(db_res)
		categories = db.execute("SELECT c.id, c.name, genre FROM categories c JOIN genres g ON c.genre = g.id").fetchall()
		return render_template("manage.html", **locals())

	table = request.form.get("table")
	action = request.form.get("action")
	if (table not in ["genres", "categories", "people"]) and (action not in ["add", "update", "delete"]):
		abort(400) # client error: bad request
	
	name  = request.form.get("name")
	genre = request.form.get("genre")
	ID    = request.form.get("id")
	if table == "genres":
		if action == "add":
			if not name:
				abort(400)
			if db.execute("SELECT * FROM genres WHERE name = ?", (name,)).fetchone():
				abort(400)
			db.execute("INSERT INTO genres (name) VALUES (?)", (name,))
		elif action == "update":
			if (not name) or (not ID):
				abort(400)
			if not db.execute("SELECT * FROM genres WHERE id = ?", (ID,)).fetchone():
				abort(400)
			db.execute("UPDATE genres SET name = ? WHERE id = ?", (name, ID))
		elif action == "delete":
			if not ID:
				abort(400)
			if not db.execute("SELECT * FROM genres WHERE id = ?", (ID,)).fetchone():
				abort(400)
			db.execute("DELETE FROM genres WHERE id = ?", (ID,))

	elif table == "categories":
		if action == "add":
			if (not name) or (not genre):
				abort(400)
			if db.execute("SELECT * FROM categories WHERE name = ? AND genre = ?", (name, genre)).fetchone():
				abort(400)
			db.execute("INSERT INTO categories (name, genre) VALUES (?, ?)", (name, genre))
		elif action == "update":
			if (not name) or (not genre):
				abort(400)
			if not db.execute("SELECT * FROM categories WHERE id = ?", (ID,)).fetchone():
				abort(400)
			db.execute("UPDATE categories SET name = ?, genre = ? WHERE id = ?", (name, genre, ID))
		elif action == "delete":
			if not ID:
				abort(400)
			if not db.execute("SELECT * FROM categories WHERE id = ?", (ID),).fetchone():
				abort(400)
			db.execute("DELETE FROM categories WHERE id = ?", (ID,))

	elif table == "people":
		if action == "add":
			if not name:
				abort(400)
			if db.execute("SELECT * FROM people WHERE name = ?", (name,)).fetchone():
				abort(400)
			db.execute("INSERT INTO people (name) VALUES (?)", (name,))
		elif action == "update":
			if (not name) or (not ID):
				abort(400)
			if not db.execute("SELECT * FROM people WHERE id = ?", (ID,)).fetchone():
				abort(400)
			db.execute("UPDATE people SET name = ? WHERE id = ?", (name, ID))
		elif action == "delete":
			if not ID:
				abort(400)
			if not db.execute("SELECT * FROM people WHERE id = ?", (ID,)).fetchone():
				abort(400)
			db.execute("DELETE FROM people WHERE id = ?", (ID,))

	db.commit()
	return redirect(request.path, 303)


@bp.route("/stats")
def stats():
	db = get_db()
	people = db.execute("SELECT id, name FROM people").fetchall()
	genres = db.execute("SELECT id, name FROM genres").fetchall()
	categories = db.execute("SELECT c.id, c.name, g.name AS genreName FROM categories c JOIN genres g ON c.genre = g.id").fetchall()
	samples = db.execute(
		"SELECT p.name AS person, c.name AS category, g.name AS genreName, s.stamp AS time FROM samples AS s JOIN categories c ON c.id = s.category JOIN genres g ON g.id = c.genre JOIN people p ON p.id = s.person ORDER BY s.stamp DESC"
	).fetchall()

	reports = []
	for genre in genres:
		perperson = []
		gsamples = [s for s in samples if s["genreName"] == genre["name"]]
		if len(gsamples) == 0:
			continue
		for person in people:
			histogram = []
			psamples = [s for s in gsamples if s["person"] == person["name"]]
			if len(psamples) == 0:
				continue
			for category in categories:
				csamples = [s for s in psamples if s["category"] == category["name"]]
				if len(psamples) == 0 or len(csamples) == 0:
					continue
				histogram.append((category["name"], len(csamples)*100/len(psamples)))
			if len(histogram) != 0:
				perperson.append({"name": person["name"], "histogram": histogram})
		if len(perperson) != 0:
			reports.append({"genreName": genre["name"], "people": perperson})
	
	return render_template("reports.html", samples=samples[0:100], reports=reports)

	# format for reports:
	# reports [
	#   {
	#     genreName: "",
	#     people: [
	#	    {
	#         name: "",
	#         histogram: {
	#           (category, percent)
	#         }
	#       }
	#     ]
	#   }
	# ]