# Video finder 

This Python program `Video Finder` is a program which can identify the source video and frame location from just a snippet. Simply preprocess some source videos and send in query videos. 

## Description

The `Video Finder` program utilizes the image hash library by taking the rgb file of a video and hashing each individual frame. The audio for the video is also sampled and audio fingerprints are generated for each frame as well. The each set of hash and fingerprint are stored within a postgresql database for searching. The query videos themselves need to be an exact match in terms of size and play speed. Upon locating the video the program will then use the mean square difference of the mp4s of the query and source video to identify the starting frame and play the source video from said frame.

## Requirements

- Python (3.x recommended)
- Required Python packages: `librosa`, `numpy`, `scipy`, `opencv-python`, `imagehash`, `ffmpeg-python`, `psycopg2`

## Usage

To run the program, run the script with the following three possible commands:
- Preprocess an entire directory:
    - python videofinder.py -pd VideosDirectory AudioDirectory
- Preprocess one video:
    - python videofinder.py -p VideoFile AudioFile
- Find video by hash:
    - python videofinder.py -f VideoFile AudioFile