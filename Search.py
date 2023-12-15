import cv2
import numpy as np

class Search:
    width = 352
    height = 288

    def __init__(self):
        self.temp = "temp"

    # Search for a specific start frame
    def get_start_frame(self, video_path, query_path, frame_num, frame_window, search_length):
        # Open video streams
        video = cv2.VideoCapture(str(video_path))
        query = cv2.VideoCapture(str(query_path))

        # Check if video streams are opened successfully
        if (video.isOpened() == False or query.isOpened() == False):
            print("Error opening video stream or file")

        # Get frames per second and total frame count
        fps = int(video.get(cv2.CAP_PROP_FPS))
        total_frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        # Read the first frame of the query video
        ret, q_frame = query.read()
        cv2.imwrite("q_frame.jpg", q_frame)

        init_frame = frame_num
        # Read until the video is completed
        while(video.isOpened()):
            # Read individual frames
            diff = (frame_num - frame_window)
            if diff < 0:
                diff = 0
            video.set(cv2.CAP_PROP_POS_FRAMES, diff)
            ret, v_frame = video.read()
            if ret == True:
                # Compare frames using mean square error
                if self.mean_square_error(q_frame, v_frame) == 0:
                    return (frame_num - frame_window - 1)

                frame_num += 1
                if frame_num > init_frame + search_length:
                    return -1
                if frame_num == total_frame_count:
                    break
            else:
                break

        # Release video streams
        video.release()
        cv2.destroyAllWindows()

        return -1

    # Calculate mean square error between two frames
    def mean_square_error(self, frame1, frame2):
        error = np.sum(cv2.subtract(frame1, frame2) ** 2)
        error /= float(frame1.shape[0] * frame1.shape[1])
        return error
