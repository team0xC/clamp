-- This is no longer needed
-- Replaced by models.py


CREATE TABLE service (
	id			INTEGER PRIMARY KEY,
	name		TEXT NOT NULL,
	port		INTEGER NOT NULL
);


CREATE TABLE vulnerability (
	id 			INTEGER PRIMARY KEY,
	service		INTEGER REFERENCES service NOT NULL,
	benign		INTEGER DEFAULT 0,
	patched		INTEGER DEFAULT 0,
	sequence	BLOB NOT NULL --copy of requests and responses from logs
	-- don't need "weaponized" field; just look for linked expoits
	-- don't need "open" field; if it's not patched, it's open
);


CREATE TABLE exploit (
	id				INTEGER PRIMARY KEY,
	vulnerability	INTEGER REFERENCES vulnerability,
	service			INTEGER REFERENCES service NOT NULL,
	path			TEXT NOT NULL,
	flag_ct_rd		INTEGER DEFAULT 0,
	flag_ct_cum		INTEGER DEFAULT 0
);
