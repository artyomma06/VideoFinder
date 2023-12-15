import ffmpeg
from imagedominantcolor import DominantColor
import os
import shutil
import psycopg2
from io import BytesIO
from PIL import Image
import imagehash

def extract_number(filename):
    return int(''.join(filter(str.isdigit, filename)))

# https://github.com/KDJDEV/imagehash-reverse-image-search-tutorial
def twos_complement(hexstr, bits):
        value = int(hexstr,16) #convert hexadecimal to integer

		#convert from unsigned number to signed number with "bits" bits
        if value & (1 << (bits-1)):
            value -= 1 << bits
        return value
# Function to remove any adjacent values within a list, keeps every 10th adjacent value.
def removeAdjacentVals(processedresult, mindifference):
    if len(processedresult) == 0:
        return []
    reducedvals = [processedresult[0]]
    count = 0
    for i in range(1, len(processedresult)):
        if abs(processedresult[i] - processedresult[i-1] > mindifference):
            reducedvals.append(processedresult[i])
            count = 0
        elif mindifference == 10:
            count = count + 1

        if count == 5:
            reducedvals.append(processedresult[i])
    return reducedvals