# Created by Antropov N.A. 14.11.19
import cv2


class VideoMaker:
    """Class provides working with video and voice
       Arguments: video_path - path to the video
                  velocity  - encoder rotation rate
                  frame_time - time for playing one frame in ms"""
    def __init__(self, video_path, rate=0, frame_time=25):

        self.video_path = video_path
        self.video = cv2.VideoCapture(self.video_path)
        self.rate = rate
        self.frame_time = frame_time

    def set_speed(self, k):
        """Method to calculate frame time in ms
           Arguments: k - converting coefficient"""
        self.frame_time = 25-self.rate*k

    def play(self):
        """Method to play video"""
        while self.video.isOpened():

            ret, frame = self.video.read()
            cv2.imshow('video', frame)
            if cv2.waitKey(self.frame_time) & 0xFF == ord('q'):
                break

        self.video.release()
        cv2.destroyAllWindows()
