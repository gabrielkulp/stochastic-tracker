# Application factory and Python's package marker
import os
from flask import Flask

def create_app():
	# create and configure the app
	app = Flask(__name__, instance_relative_config=True)
	
	app.config.from_mapping(
		SECRET_KEY="dev",
		DATABASE=os.path.join(app.instance_path, "samples.sqlite"),
		BASIC_AUTH_USERNAME=os.environ.get("AUTH_USERNAME"),
		BASIC_AUTH_PASSWORD=os.environ.get("AUTH_PASSWORD")
	)

	app.config.from_pyfile("config.py", silent=True)

	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	from . import db
	db.init_app(app)

	from . import pages
	app.register_blueprint(pages.bp)
	#app.add_url_rule("/", endpoint="home")

	from flask_basicauth import BasicAuth
	basic_auth = BasicAuth(app)
	if app.config["BASIC_AUTH_USERNAME"] and app.config["BASIC_AUTH_PASSWORD"]:
		app.config["BASIC_AUTH_FORCE"] = True
	return app
