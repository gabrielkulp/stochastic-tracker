from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for, abort
)
import urllib.request, urllib.error
import json

from werkzeug.exceptions import abort

from tracker.db import get_db

bp = Blueprint('pages', __name__)

@bp.route("/")
def index():
	return redirect(url_for("pages.home"), 303)


@bp.route("/home", methods=["GET", "POST"])
def home():
	db = get_db()
	if (request.method == "GET"):
		people = db.execute("SELECT id, name FROM people").fetchall()
		genres = db.execute("SELECT id, name FROM genres").fetchall()
		categories = db.execute("SELECT c.id, c.name, g.name AS genreName FROM categories c JOIN genres g ON c.genre = g.id").fetchall()
		return render_template("home.html", **locals())
	
	person = request.form.get("person")
	category = request.form.get("category")
	if (not person) or (not category):
		abort(400) # client error: bad request
	
	db.execute("INSERT INTO samples (person, category) VALUES (?, ?)", (person, category))
	db.commit()
	return redirect(url_for("pages.home"), 303)


@bp.route("/manage", methods=["GET", "POST"])
def manage():
	db = get_db()
	if (request.method == "GET"):
		people = db.execute("SELECT id, name FROM people").fetchall()
		genres = db.execute("SELECT id, name FROM genres").fetchall()
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


@bp.route("/reports")
def reports():
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