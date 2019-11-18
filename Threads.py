import threading
import multiprocessing as mp
import subprocess
import time

from ArduinoSerial import ArduinoSerial, RCSerial
from VideoMaker import VideoMaker


class VideoThread(threading.Thread):
    """Class provides working with main thread - video playing
       Arguments: path_one - path to the first video
                  path_two - path to the second video
                  state - system state"""
    def __init__(self, path_one, path_two, state, k):

        threading.Thread.__init__(self)
        self.video_one = VideoMaker(path_one)
        self.video_two = VideoMaker(path_two)
        self.state = state
        self.play_state_list = [0, 1, 2]
        self.k = k

    def run(self):

        if self.state in self.play_state_list:

            self.video_one.play()

        elif self.state == 2:

            self.change_video()
            self.state = 3

        elif self.state == 3:

            self.video_one.set_speed(self.k)
            self.video_one.play()

    def change_video(self):

        pass


class ArduinoThread(threading.Thread):
    """Class provides working with the first sub thread - connection with arduino
       Arguments: state - system state"""
    def __init__(self, state):

        threading.Thread.__init__(self)
        self.ino_ser = ArduinoSerial()
        self.state = state
        self.send_state_list = [1, 3, 5]

    def run(self):

        while True:

            if self.state in self.send_state_list:

                self.ino_ser.send_data(self.state)

                msg = self.ino_ser.get_data()

                if msg == "OK":

                    self.state += 1

                if self.state


class RCThread(threading.Thread):
    """Class provides working with the second sub thread - connection with main controller
       Arguments: state - system state"""
    def __init__(self, state):

        threading.Thread.__init__(self)
        self.rc_ser = RCSerial()  # Main controller serial port init
        self.state = state
        #  System action dictionary
        self.action_dict = {"Start": self.state_change, "OK": self.confirm, "Timeout": self.stop_process}

    def run(self):

        while True:

            msg = self.rc_ser.get_data()

            self.action_dict[msg]()

    def state_change(self):
        """"Method to confirm getting message from main controller and to change system state"""
        self.rc_ser.send_data()
        self.state += 1

    def confirm(self):
        """Method to do nothing when there is confiming message from main controller"""
        pass

    def stop_process(self):
        """Method to stop all system because of timeout"""
        self.state = 0
