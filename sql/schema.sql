-- Your database schema goes here --
DROP TABLE IF EXISTS hashes;

CREATE TABLE hashes(
	id UUID UNIQUE PRIMARY KEY DEFAULT gen_random_uuid(),
	videoname VARCHAR(50),
	imagehash VARCHAR,
	audiohash VARCHAR,
	framenumber int
);

