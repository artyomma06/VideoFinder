import psycopg2
from utils import removeAdjacentVals

# Replace 'your_host', 'your_database', 'your_user', and 'your_password' with your actual database information
conn = psycopg2.connect(
    host='localhost',  # PostgreSQL server assumed to be running on the local machine
    database='postgres',
    user='postgres',
    password='postgres',
    port=5432  # Port number specified in your Docker Compose file
)

# Store hashes of a single file in the database
def storeHashesOneFile(filename, hashes):
    cursor = conn.cursor()
    query = "INSERT INTO hashes (videoname, imagehash, audiohash, framenumber) VALUES (%s, %s, %s, %s)"
    for i in hashes:
        cursor.execute(query, (filename, i["imagehash"], i["audiohash"], i["framenumber"]))
    conn.commit()
    cursor.close()
    conn.close()

# Store hashes of multiple files in the database
def storeHashDir(results):
    cursor = conn.cursor()
    query = "INSERT INTO hashes (videoname, imagehash, audiohash, framenumber) VALUES (%s, %s, %s, %s)"
    for result in results:
        for i in result["hashes"]:
            cursor.execute(query, (result["videoName"], i["imagehash"], i["audiohash"], i["framenumber"]))
    conn.commit()
    cursor.close()
    conn.close()

# Find videos in the database based on image hashes
def findVideoByHash(hashes):
    cursor = conn.cursor()
    query = "SELECT distinct videoname, COUNT(DISTINCT imagehash) AS total_count FROM hashes WHERE imagehash IN (%s, %s, %s, %s, %s) GROUP BY videoname, imagehash ORDER BY videoname, total_count DESC;"
    cursor.execute(query, (hashes[0]["imagehash"], hashes[1]["imagehash"], hashes[2]["imagehash"], hashes[3]["imagehash"], hashes[4]["imagehash"]))
    result = cursor.fetchall()
    cursor.close()
    return result

# Find frames in a video based on image and audio hashes
def findFrameByHash(videoname, hashdict, audihash):
    cursor = conn.cursor()
    query = "SELECT framenumber from hashes h where videoname = %s and imagehash = %s order by framenumber asc;"
    cursor.execute(query, (videoname, hashdict["imagehash"]))
    result = cursor.fetchall()
    processedresult = [number for tup in result for number in tup]
    reducedimagevals = removeAdjacentVals(processedresult, 1)
    reducedimagevals = removeAdjacentVals(reducedimagevals, 10)

    query = "SELECT framenumber from hashes h where videoname = %s and audiohash = %s order by framenumber asc;"
    cursor.execute(query, (videoname, audihash))
    result = cursor.fetchall()
    
    processedresult = [number for tup in result for number in tup]
    reducedaudiovals = removeAdjacentVals(processedresult, 1)
    reducedaudiovals = removeAdjacentVals(reducedaudiovals, 10)
    reducedaudiovals = [[element, "aud"] for element in reducedaudiovals]
    reducedimagevals = [[element, "vid"] for element in reducedimagevals]
    reducedvals = reducedaudiovals + reducedimagevals
    if len(reducedimagevals) < len(reducedaudiovals):
        reducedvals = reducedimagevals + reducedaudiovals

    cursor.close()
    conn.close()
    return reducedvals
