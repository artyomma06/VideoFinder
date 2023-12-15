import os
import shutil
import time
import math
from PIL import Image
import imagehash
import ffmpeg
from utils import extract_number, process_file, process_first, twos_complement, display_video
import db  # Assuming that db is a module in your project
from Search import Search  # Assuming that Search is a class in your Search module
import argparse
import sys

class Finder:
    def __init__(self):
        self.temp = ""
        self.search = Search()  # Create an instance of the Search class

    # Method to create frames from a video file
    def makeFrames(self, input_file, output_folder, fps=None):
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)
        os.makedirs(output_folder, exist_ok=True)
        output_pattern = os.path.join(output_folder, 'frame%d.png')
        if fps is None:
            ffmpeg.input(input_file, pix_fmt='rgb24', s='352x288').output(output_pattern).run()
        else:
            rate = 'fps='+str(fps)
            ffmpeg.input(input_file, pix_fmt='rgb24', s='352x288').output(output_pattern, vf=rate, r=fps).run()

    # Method to create a video hash
    def makeVideoHash(self, vidpath, audpath):
        self.makeFrames(vidpath, "hashDump")
        hashes = []
        filenames = os.listdir("hashDump")
        sorted_frames = sorted(filenames, key=extract_number)
        frames = [os.path.join("hashDump", filename) for filename in sorted_frames]
        audio_hash = process_file(audpath)
        num = 0
        for frame in frames:
            with open(frame, "rb") as imageBinary:
                img = Image.open(imageBinary)
                imgHash = str(imagehash.dhash(img))
                hashInt = twos_complement(imgHash, 64)  # convert from hexadecimal to 64-bit signed integer
                try:
                    hashes.append({"framenumber": num, "imagehash": hashInt, "audiohash": audio_hash[num]})
                except:
                    hashes.append({"framenumber": num, "imagehash": hashInt, "audiohash": audio_hash[-1]})
                num = num + 1
        shutil.rmtree("hashDump")
        return hashes

    # Method to preprocess and store hash for a single video file
    def preProcessHash(self, videopath, audiopath):
        hashes = self.makeVideoHash(videopath, audiopath)
        sprite = ""
        try:
            sprite = videopath.split("/")[-1]
            sprite = sprite.split(".")[0]
        except:
            sprite = videopath.split(".")[0]
        db.storeHashesOneFile(sprite, hashes)
        return "success"

    # Method to preprocess and store hash for a directory of video files
    def preProcessHashDirectory(self, videodir, audiodir):
        files = os.listdir(videodir)
        res = []
        for file in files:
            filename = file.split(".")[0]
            vidpath = videodir + "/" + filename + ".rgb"
            audpath = audiodir + "/" + filename + ".wav"
            hashvals = self.makeVideoHash(vidpath, audpath)
            res.append({"videoName": filename, "hashes": hashvals})
        db.storeHashDir(res)
        return "success"

    # Method to find a video by hash
    def findVideoByHash(self, videopath, audiopath):
        start_time = time.time()
        self.makeFrames(videopath, "hashDump", 1)
        hashes = []
        filenames = os.listdir("hashDump")
        sorted_frames = sorted(filenames, key=extract_number)
        frames = [os.path.join("hashDump", filename) for filename in sorted_frames]
        num = 0
        first_point = frames[0]
        last_point = frames[-1]
        middle_index = len(frames) // 2
        middle_point = frames[middle_index]
        midpoint_first_middle = frames[len(frames) // 4]
        midpoint_middle_last = frames[len(frames) // 4 + middle_index]
        frames = [first_point, midpoint_first_middle, middle_point, midpoint_middle_last, last_point]
        for frame in frames:
            with open(frame, "rb") as imageBinary:
                num = num + 1
                img = Image.open(imageBinary)
                imgHash = str(imagehash.dhash(img))
                hashInt = twos_complement(imgHash, 64)
                hashes.append({"framenumber": num, "imagehash": str(hashInt), "audiohash": 0})
        shutil.rmtree("hashDump")
        video = db.findVideoByHash(hashes)
        video = video[0][0]
        firstframe = hashes[0]
        firstaud = process_first(audiopath, 0)
        matchingframes = db.findFrameByHash(video, firstframe, firstaud)
        for i in range(len(matchingframes)):
            sprite = ""
            try:
                sprite = videopath.split("/")[-1]
                sprite = sprite.split(".")[0]
            except:
                sprite = videopath.split(".")[0]
            found_frame = -1
            if matchingframes[i][1] == "aud":
                found_frame = self.search.get_start_frame('Videos/' + video + '.mp4', 'Queries/' + sprite + '.mp4', matchingframes[i][0], 1, 3)
            else:
                found_frame = self.search.get_start_frame('Videos/' + video + '.mp4', 'Queries/' + sprite + '.mp4', matchingframes[i][0], 20, 60)
            if found_frame != -1:
                print("Frame: " + str(found_frame))
                print("Frame: %02d:%02d:%02d" % (math.floor((found_frame/30)/60), math.floor((found_frame/30)%60), found_frame%30))
                end_time = time.time()
                elapsed_time = end_time - start_time
                print(f"Program execution time: {elapsed_time:.2f} seconds")
                # found_frame = 10 * ((found_frame + 10 - 1) // 10) # may or may not keep depending on what TA says
                display_video('Videos/' + video + '.mp4', found_frame)
                break

def main():
    parser = argparse.ArgumentParser(description='Video Finder Script')

    # Add flags
    parser.add_argument('-pd', '--preprocess_directory', action='store_true', help='Preprocess a directory')
    parser.add_argument('-p', '--preprocess', action='store_true', help='Preprocess a file')
    parser.add_argument('-f', '--find', action='store_true', help='Find video by hash')

    # Add additional parameters
    parser.add_argument('video_file', type=str, help='Path to the video file')
    parser.add_argument('audio_file', type=str, help='Path to the audio file')

    args = parser.parse_args()

    finder = Finder()

    if args.preprocess_directory:
        finder.preProcessHashDirectory(args.video_file, args.audio_file)
    elif args.preprocess:
        finder.preProcessHash(args.video_file, args.audio_file)
    elif args.find:
        finder.findVideoByHash(args.video_file, args.audio_file)

if __name__ == "__main__":
    main()