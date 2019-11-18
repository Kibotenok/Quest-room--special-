import threading

from ArduinoSerial import ArduinoSerial, RCSerial
from VideoControl import VideoControl

VIDEO_PATH_ONE = ''
VIDEO_PATH_TWO = ''


class VideoThread(threading.Thread):
    """Class provides working with main thread - video playing
       Arguments: path_one - path to the first video
                  path_two - path to the second video
                  state_list - system state list
                  state - current system state
                  k - coefficient to convert encoder rate to video frame time"""
    def __init__(self, path_one, path_two, state_list, k):

        threading.Thread.__init__(self)
        self.video_one = VideoMaker(path_one)  # first video
        self.video_two = VideoMaker(path_two)  # second video
        self.state_list = state_list
        self.k = k

    def run(self):
        global state
        while True:

            if state == 1:

                pass

            elif state in [2, 3]:

                self.video_one.play()

            elif state == 4:

                self.change_video()
                lock.acquire()
                state += 1
                lock.release()

            elif state in [5, 6]:

                self.video_one.rate = rate
                self.video_one.set_speed(k=self.k)
                self.video_one.play()

            elif state == 7:
                lock.acquire()
                state = 1
                lock.release()

            elif state == 8:

                print("Time is over. System is returning to its first state\n")
                lock.acquire()
                state = 1
                lock.release()

            else:

                print("State value error. System is returning to its first state\n")
                lock.acquire()
                state = 1
                lock.release()

    def change_video(self):

        pass


class ArduinoThread(threading.Thread):
    """Class provides working with the first sub thread - connection with arduino
       Arguments: state_list - system state list
                  state - current system state"""
    def __init__(self, state_list):

        threading.Thread.__init__(self)
        self.ino_ser = ArduinoSerial()  # Serial port init
        self.state_list = state_list
        self.send_msg = {2: 'Start\n', 4: 'OK\n', 5: 'Next\n', 7: 'Stop\n'}  # Dict of messages sent to arduino
        self.get_msg = 'Change\n'  # Received message from arduino
        self.flag = True

    def run(self):

        global state
        global rate

        while True:

            if state == 1:

                self.flag = True

            if state == 3:

                try:

                    msg = self.ino_ser.get_data()

                    if msg == self.get_msg:

                        lock.acquire()
                        state += 1
                        lock.release()

                except (NameError, TimeoutError):

                    pass

            if state in self.send_msg.keys():

                if state == 4:
                    # We need send message only once in this state
                    if self.flag:

                        self.ino_ser.send_data(msg=self.send_msg[state])
                        self.flag = False

                else:

                    self.ino_ser.send_data(msg=self.send_msg[state])

                    if self.ino_ser.get_response():
                        # If it is final state, return to begin
                        # Else go to the next state
                        if state == 7:

                            lock.acquire()
                            state = 1
                            lock.release()

                        else:

                            lock.acquire()
                            state += 1
                            lock.release()

            if state == 6:

                try:
                    # Get encoder rate
                    lock.acquire()
                    rate = self.ino_ser.get_data()
                    lock.release()

                except (NameError, TimeoutError):

                    pass

            if state == 8:
                # Time is over. Return to begin
                self.ino_ser.send_data(msg=self.send_msg[state])

                if self.ino_ser.get_response():

                    lock.acquire()
                    state = 1
                    lock.release()


class RCThread(threading.Thread):
    """Class provides working with the second sub thread - connection with main controller
       Arguments: state_list - system state list
                  state - current system state"""
    def __init__(self, state_list):

        threading.Thread.__init__(self)
        self.rc_ser = RCSerial()  # Main controller serial port init
        self.state_list = state_list
        self.state = state
        #  System action dictionary
        self.action_dict = {"Start\n": self.state_change, "Timeout\n": self.stop_process}

    def run(self):

        global state

        while True:

            if state in [5, 7]:

                self.rc_ser.send_data('complete')

            else:

                try:
                    msg = self.rc_ser.get_data()

                    if msg in self.action_dict.keys():

                        self.action_dict[msg]()

                except (NameError, TimeoutError):

                    pass

    def state_change(self):
        """Method to change system state"""

        global state

        lock.acquire()
        state += 1
        lock.release()

    def stop_process(self):
        """Method to return system to its begin state"""
        global state

        lock.acquire()
        state = 1
        lock.release()


if __name__ == '__main__':

    # State list
    state_list = [1, 2, 3, 4, 5, 6, 7, 8]
    # First system state
    state = 1
    # Coefficient to convert encoder rate to video frame time
    k = 1
    # Encoder default rate
    rate = 0

    lock = threading.RLock()

    # Threads init
    main_thread = VideoThread(path_one=VIDEO_PATH_ONE, path_two=VIDEO_PATH_TWO, state_list=state_list, k=1)
    ino_thread = ArduinoThread(state_list=state_list)
    rc_thread = RCThread(state_list=state_list)

    main_thread.setDaemon(True)
    ino_thread.setDaemon(True)
    rc_thread.setDaemon(True)

    # Threads start
    main_thread.start()
    ino_thread.start()
    rc_thread.start()
