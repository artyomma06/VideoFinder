-- Index Your Tables Here --
CREATE INDEX idx_imagehash_videoname ON hashes (imagehash, videoname);
CREATE INDEX idx_videoname_imagehash_framenumber ON hashes (videoname, imagehash, framenumber);
CREATE INDEX idx_videoname_audiohash_framenumber ON hashes (videoname, audiohash, framenumber);
