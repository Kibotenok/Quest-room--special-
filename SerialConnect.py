#  Created by Antropov N.A. 12.11.19
import serial
from serial.tools import list_ports
import time


class ArduinoSerial:
    """Class provides work with arduino serial port
       Arguments: state - system state
                  baudrate - connection rate"""
    
    def __init__(self, state=1, baudrate=9600):
        
        self.port = self.port_find()  # Arduino port name
        self.state = state  # System state
        self.baudrate = baudrate
        self.ino_ser = serial.Serial(port=self.port, baudrate=self.baudrate)  # Serial object
        self.init_ser()  # Serial connection init
        self.in_msg_dict = {"OK": [], "Change": 2}  # Message dictionary from arduino
        self.out_msg_dict = {1: "Start", 2: "Next", 3: "Stop", 4: "OK", 5: "Timeout"}  # Message dictionary to arduino

    def port_find(self):
        """Method to find arduino port name
           Return port name"""
        try:
            ports = list_ports.comports()

            for port, desc, hwid in sorted(ports):

                if hwid.find('0403') != -1:
                   arduino_port = port

            print("Port name is ", arduino_port, "\n")
            return arduino_port
        
        except NameError:
            
            print("No connection betweeen arduino and raspberry\n")

    def init_ser(self):
        """Method to init serial connection
           Return nothing"""
        try_counter = 1
        
        while True:
            try:
                if self.ino_ser.isOpen():

                    self.ino_ser.close()

                self.ino_ser.open()
                time.sleep(3)
                print("Serial port is availble. Connection is ready\n")
                break

            except (OSError, serial.SerialException):

                print("Port opening error. Try again\n")
                try_counter += 1

                if try_counter == 10:

                    print("Port is unavailable\n")
                    break

                else:
                    continue

    def send_data(self, state):
        """Method to send data to arduino depending on system state
           Return nothing"""
        states = self.out_msg_dict.keys()

        if self.state in states:

            message = self.out_msg_dict[self.state]
            self.ino_ser.write(message)

        else:

            print("State value error. System go back to begin state\n")
            self.state = 1

    def get_data(self):
        """Method to get data from arduino
           Return getting data"""
        try:

            pass

        except TimeoutError:

            pass

    def change_state(self):
        """Method to change system state
           Return state value"""
        pass


class RCSerial:
    """"Class provides working with rc serial port"""
    def __init__(self):

        self.port = self.port_find()
        self.in_msg_dict = {"start": 1, "timeout": 5}
        self.out_msg_dict = {1: "finish one", 2: "finish two"}

    def port_find(self):
        """Method to find rc port name
           Return port name"""
        try:
            ports = list_ports.comports()

            for port, desc, hwid in sorted(ports):

                if hwid.find('0403') != -1:
                    rc_port = port

            print("Port name is ", rc_port, "\n")
            return rc_port

        except NameError:

            print("No connection betweeen main controller and raspberry\n")

    def init_ser(self):
        """Method to init serial connection
           Return nothing"""
        try_counter = 1

        while True:
            try:
                if self.ino_ser.isOpen():
                    self.ino_ser.close()

                self.ino_ser.open()
                time.sleep(3)
                print("Serial port is availble. Connection is ready\n")
                break

            except (OSError, serial.SerialException):

                print("Port opening error. Try again\n")
                try_counter += 1

                if try_counter == 10:

                    print("Port is unavailable\n")
                    break

                else:
                    continue

    def send_data(self):
        """Method to send data to arduino depending on system state
           Return nothing"""
        states = self.out_msg_dict.keys()

        if self.state in states:

            message = self.out_msg_dict[self.state]
            self.ino_ser.write(message)

        else:

            print("State value error. System go back to begin state\n")
            self.state = 1

    def get_data(self):
        """Method to get data from arduino
           Return getting data"""
        try:

            pass

        except TimeoutError:

            pass

    def change_state(self):
        """Method to change system state
           Return state value"""
        pass
