# Created by Antropov N.A.
# Main script for the puzzle in the quest room
from multiprocessing import Process, JoinableQueue, RLock, Value
import cv2
import time
import vlc
from omxplayer.player import OMXPlayer

from SerialConnection import SerialConnection

# Paths to media
VIDEO_FIRST_PATH = '/home/pi/Desktop/Quest_final/space.mp4'
VIDEO_SECOND_PATH = '/home/pi/Desktop/Quest_final/eye.mp4'
IMAGE_PATH = '/home/pi/Desktop/Quest_final/black.jpg'


def setFrameTime(rot_dir, min_val, max_val, rate):
    """Calculate video rate depending on encoder rotation direction


       :param rot_dir: encoder rotation direction
       :param min_val: minimum available video rate value
       :param max_val: maximum available video rate value
       :param rate: current video rate value

       Return new video rate value
    """

    if rot_dir:
        
        rate += 0.1
        
        if rate >= max_val:
            return max_val
        else:
            return round(rate, 2)
    else:
        rate -= 0.1

        if rate <= min_val:
            return min_val
        else:
            return round(rate, 2)
    

def changeVideo(path, win, image):
    """Show sub video by using Omxplayer


       :param path: path to the video
       :param win: window name
       :param image: last video frame
    """

    player_one = OMXPlayer(path)
    time.sleep(2.5)
    cv2.imshow(win, image)
    cv2.waitKey(25)
    player_one.quit()


def rcProcess(state, lock, rate_q, change_q):
    """Provide work with rc serial port


       :param state: current system state
       :param lock: lock for global variables
       :param rate_q: queue with video rate value
       :param change_q: queue with video change flag
    """

    state_list = [1, 2, 3, 5]
    rc_ser = SerialConnection(device_name='RC', device_id='1411')  # Create rc serial connection
    flag = True
    prev_rate = 0

    while True:

        if state.value in state_list:

            if state.value == 1:
                # Wait for start command

                flag = True

                if rc_ser.ser.inWaiting() > 0:
                    msg = rc_ser.getData()

                    if b'1000' in msg:

                        lock.acquire()
                        state.value = 2
                        lock.release()

            elif state.value == 2:
                # Check special commands

                if rc_ser.ser.inWaiting() > 0:
                    msg = rc_ser.getData()

                    if b'5000' in msg:
                        # Quest timeout command
                        lock.acquire()
                        state.value = 8
                        lock.release()

                    elif b'6000' in msg:
                        # Quest trouble end
                        lock.acquire()
                        state.value = 4
                        lock.release()

            elif state.value == 3:
                # Check special commands

                if rc_ser.ser.inWaiting() > 0:
                    msg = rc_ser.getData()

                    if b'5000' in msg:

                        lock.acquire()
                        state.value = 8
                        lock.release()

                    elif b'6000' in msg:

                        lock.acquire()
                        state.value = 4
                        lock.release()

                # Send data from Arduino
                if not (rate_q.empty()):
                    # Send new video rate value

                    rate = rate_q.get()
                    if not(prev_rate == rate) and (rate % 0.2 == 0):
                        rc_ser.sendData(msg=rate, flag=True)
                        prev_rate = rate

                if not (change_q.empty()):
                    # Send message about sub video

                    if change_q.get():

                        rc_ser.sendData(msg=b'2000')

            elif state.value == 5:

                if flag:
                    # Send end command
                    rc_ser.sendData(msg=b'4000')
                    flag = False

                # Check special command
                if rc_ser.ser.inWaiting() > 0:
                    msg = rc_ser.getData()

                    if b'5000' in msg:
                        lock.acquire()
                        state.value = 8
                        lock.release()


def inoProcess(state, lock, rate_q_rc, change_q_rc, rate_q_pi, change_q_pi, min_val, max_val):
    """Provide work with arduino serial port


       :param state: current system state
       :param lock: lock for global variables
       :param rate_q_rc: queue with video rate value for rc
       :param change_q_rc: queue with video change flag for rc
       :param rate_q_pi: queue with video rate value for pi
       :param change_q_pi: queue with video change flag for pi
       :param min_val: minimum available video rate value
       :param max_val: maximum available video rate value
    """

    state_list = [2, 3, 4, 8]
    ino_ser = SerialConnection(device_name='Arduino', device_id='1733')  # Create arduino serial connection
    prev_rate = min_val

    while True:

        if state.value in state_list:

            if state.value == 2:
                # Send start command to Arduino
                ino_ser.sendData(msg=b'S')

                lock.acquire()
                state.value = 3
                lock.release()

            if state.value == 3:
                # Get data from Arduino

                if ino_ser.ser.inWaiting() > 0:
                    msg = ino_ser.getData()

                    if not (b'None' in msg):

                        if b'Change' in msg:

                            change_q_rc.put(True)
                            change_q_pi.put(True)

                        elif b'Up' in msg:
                            rate = setFrameTime(True, min_val, max_val, prev_rate)

                            if not(prev_rate == rate):
                                rate_q_pi.put(rate)
                                rate_q_rc.put(rate)
                                prev_rate = rate
                        else:
                            rate = setFrameTime(False, min_val, max_val, prev_rate)

                            if not (prev_rate == rate):
                                rate_q_pi.put(rate)
                                rate_q_rc.put(rate)
                                prev_rate = rate

            if state.value == 4:
                # Send end command to Arduino
                ino_ser.sendData(msg=b'E')

                if ino_ser.getResponse():
                    lock.acquire()
                    state.value = 5
                    lock.release()

            if state.value == 8:
                # Send timeout command to Arduino
                ino_ser.sendData(msg=b'T')
                prev_rate = min_val

                if ino_ser.getResponse():

                    lock.acquire()
                    state.value = 1
                    lock.release()


def piProcess(state, lock, rate_q, change_q, first_path, second_path, third_path, timings, threshold=3.2, timer=300000,
               s_rate=0.69):
    """Provide work with media on Raspberry Pi


       :param state: current system state
       :param lock: lock for global variables
       :param rate_q: queue with video rate value
       :param change_q: queue with video change flag
       :param first_path: path to the first video
       :param second_path: path to the second video
       :param third_path: path to the image
       :param timings: list of timings with white screen in video in ms
       :param threshold: threshold value of video rate (the default is 3.2)
       :param timer: time value for looping value in ms (the default is 300000)
       :param s_rate: start video rate value (the default is 0.69)
    """

    state_list = [1, 2, 3, 4, 5, 8]
    rate = s_rate
    last_timing = 0

    # First video init by using VLC player
    Instance = vlc.Instance('--no-xlib')
    player = Instance.media_player_new()
    Media = Instance.media_new_path(first_path)
    player.set_media(Media)
    vlc.libvlc_media_player_set_rate(player, rate)
    player.set_fullscreen(True)

    # Images init
    image = cv2.imread(third_path)
    eye1 = cv2.imread('/home/pi/Desktop/Quest_final/eye.jpg')
    eye2 = cv2.imread('/home/pi/Desktop/Quest_final/eye1.jpg')
    winname = 'Quest'
    cv2.namedWindow(winname, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(winname, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:

        if state.value in state_list:

            if state.value == 1:
                # Black screen
                cv2.imshow(winname, image)
                cv2.waitKey(25)

            elif state.value == 2:
                # Start showing main video
                vlc.libvlc_media_player_set_rate(player, rate)
                player.play()
                
            elif state.value == 3:

                if not(rate_q.empty()):
                    # Change video rate value
                    rate = rate_q.get()
                    vlc.libvlc_media_player_set_rate(player, rate)

                if rate >= threshold:
                    # Quest end
                    lock.acquire()
                    state.value = 4
                    lock.release()
                    continue

                if not(change_q.empty()):
                    # Show sub video
                    if change_q.get():

                        cv2.imshow(winname, eye1)
                        cv2.waitKey(25)
                        player.stop()
                        changeVideo(second_path, winname, eye2)
                        
                    player.play()

                # Video loop
                cur_timing = vlc.libvlc_media_player_get_time(player)

                if cur_timing >= timer:
                    vlc.libvlc_media_player_set_time(player, 1000)

            elif state.value == 4:
                # Play the video to the end
                vlc.libvlc_media_player_set_rate(player, 3.5)
                vlc.libvlc_media_player_set_time(player, timer)

            elif state.value == 5:
                # Go to the last frame
                pass

            elif state.value == 8:
                cv2.imshow(winname, image)
                cv2.waitKey(25)
                player.stop()
                rate = s_rate


if __name__ == '__main__':

    # Common data for processes
    rate_q_rc = JoinableQueue()
    rate_q_pi = JoinableQueue()
    change_q_rc = JoinableQueue()
    change_q_pi = JoinableQueue()
    state = Value('i', 1)
    lock = RLock()

    # Constants
    min_val = 0.69  # Minimum video rate value
    max_val = 3.5   # Maximum video rate value
    threshold = 3.2
    timer = 320000  # Time value for loop in ms
    timings = []  # List of timings with white screen in video in ms

    # Init and start processes
    rc = Process(target=rcProcess, args=(state, lock, rate_q_rc, change_q_rc,))
    ino = Process(target=inoProcess, args=(state, lock, rate_q_rc, change_q_rc, rate_q_pi, change_q_pi, min_val,
                                            max_val,))
    rc.daemon = True
    ino.daemon = True
    rc.start()
    ino.start()

    # Start main process
    piProcess(state, lock, rate_q_pi, change_q_pi, VIDEO_FIRST_PATH, VIDEO_SECOND_PATH, IMAGE_PATH, timings, threshold,
               timer, min_val,)

    # Stop processes
    rc.join()
    ino.join()
