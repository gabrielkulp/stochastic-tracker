DROP TABLE IF EXISTS people;
DROP TABLE IF EXISTS pings;
DROP TABLE IF EXISTS metrics;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS glimpse_metrics;
DROP TABLE IF EXISTS glimpse_tags;

CREATE TABLE people (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE NOT NULL
);
INSERT INTO people (name) VALUES ("Kendrea");
INSERT INTO people (name) VALUES ("Gabriel");


CREATE TABLE pings (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	stamp DATETIME DEFAULT CURRENT_TIMESTAMP,
	person INTEGER NOT NULL,
	FOREIGN KEY (person) REFERENCES people (id) ON DELETE CASCADE
);


CREATE TABLE metrics (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE NOT NULL,
	minimum REAL,
	maximum REAL
);
INSERT INTO metrics (name, minimum, maximum) VALUES ("mood",  -1, 1);
INSERT INTO metrics (name, minimum, maximum) VALUES ("energy", 0, 1);


CREATE TABLE categories (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE NOT NULL
);
INSERT INTO categories (name, id) VALUES ("activity", 0);
INSERT INTO categories (name, id) VALUES ("location", 1);
INSERT INTO categories (name, id) VALUES ("social",   2);


CREATE TABLE tags (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	parent INTEGER NOT NULL,
	FOREIGN KEY (parent) REFERENCES categories (id) ON DELETE CASCADE,
	UNIQUE (name, parent)
);
/* activities */
INSERT INTO tags (name, parent) VALUES ("sleep",     0);
INSERT INTO tags (name, parent) VALUES ("eating",    0);
INSERT INTO tags (name, parent) VALUES ("deep work", 0);
INSERT INTO tags (name, parent) VALUES ("busy work", 0);
INSERT INTO tags (name, parent) VALUES ("transit",   0);
/* locations */
INSERT INTO tags (name, parent) VALUES ("home",      1);
INSERT INTO tags (name, parent) VALUES ("campus",    1);
INSERT INTO tags (name, parent) VALUES ("store",     1);
INSERT INTO tags (name, parent) VALUES ("K parents", 1);
INSERT INTO tags (name, parent) VALUES ("G parents", 1);
INSERT INTO tags (name, parent) VALUES ("out",       1);
/* social contexts */
INSERT INTO tags (name, parent) VALUES ("alone",     2);
INSERT INTO tags (name, parent) VALUES ("just us",   2);
INSERT INTO tags (name, parent) VALUES ("family",    2);
INSERT INTO tags (name, parent) VALUES ("friends",   2);
INSERT INTO tags (name, parent) VALUES ("public",    2);
INSERT INTO tags (name, parent) VALUES ("strangers", 2);


CREATE TABLE glimpse_metrics (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	ping INTEGER NOT NULL,
	metric INTEGER NOT NULL,
	val REAL,
	FOREIGN KEY (ping) REFERENCES pings (id) ON DELETE CASCADE,
	FOREIGN KEY (metric) REFERENCES metrics (id) ON DELETE CASCADE
);


CREATE TABLE glimpse_tags (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	ping INTEGER NOT NULL,
	tag INTEGER NOT NULL,
	FOREIGN KEY (ping) REFERENCES pings (id) ON DELETE CASCADE,
	FOREIGN KEY (tag) REFERENCES tags (id) ON DELETE CASCADE
);
