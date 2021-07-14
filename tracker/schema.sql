DROP TABLE IF EXISTS people;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS pings;
DROP TABLE IF EXISTS glimpses;

CREATE TABLE people (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE NOT NULL
);
INSERT INTO people (name) VALUES ("Gabriel");
INSERT INTO people (name) VALUES ("Kendrea");

CREATE TABLE tags (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	parent INTEGER,
	FOREIGN KEY (parent) REFERENCES tags (id),
	UNIQUE (name, parent)
);
INSERT INTO tags (name, parent) VALUES ("mood", NULL);
INSERT INTO tags (name, parent) VALUES ("activity", NULL);
INSERT INTO tags (name, parent) VALUES ("location", NULL);

CREATE TABLE pings (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	stamp DATETIME DEFAULT CURRENT_TIMESTAMP,
	person INTEGER NOT NULL,
	FOREIGN KEY (person) REFERENCES people (id)
);

CREATE TABLE glimpses (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	ping INTEGER NOT NULL,
	tag INTEGER NOT NULL,
	FOREIGN KEY (ping) REFERENCES pings (id),
	FOREIGN KEY (tag) REFERENCES tags (id)
);
