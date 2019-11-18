#  Created by Antropov N.A. 12.11.19
import serial
from serial.tools import list_ports
import time


class ArduinoSerial:
    """Class provides work with arduino serial port
       Arguments: baudrate - connection rate"""
    
    def __init__(self, baudrate=9600):
        
        self.port = self.port_find()  # Arduino port name
        self.baudrate = baudrate
        self.ino_ser = serial.Serial(port=self.port, baudrate=self.baudrate)  # Serial object
        self.init_ser()  # Serial connection init

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

    def send_data(self, msg):
        """Method to send data to arduino
           Arguments: msg - message to send
           Return nothing"""
        self.ino_ser.write(msg)

    def get_data(self):
        """Method to get data from arduino
           Return getting data"""
        try:
            while self.ino_ser.inWaiting() > 0:

                data = self.ino_ser.read_until()

                return data

        except TimeoutError:

            pass

    def get_response(self):

        msg = self.get_data()

        if msg == 'OK':

            return True

        return False


class RCSerial:
    """"Class provides working with rc serial port
        Arguments: baudrate - connection rate"""
    def __init__(self, baudrate=9600):

        self.port = self.port_find()  # Rc port name
        self.own_address = self.find_address()  # Raspberry Pi address
        self.baudrate = baudrate
        self.complete_quest = 0  # complete quest count
        self.rc_ser = serial.Serial(port=self.port, baudrate=self.baudrate)  # Serial object
        self.init_ser()  # Serial port init

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

            print("No connection between main controller and raspberry\n")

    def find_address(self):
        """Method to find raspberry pi address
           Return device address"""
        address = ''
        return address

    def init_ser(self):
        """Method to init serial connection
           Return nothing"""
        try_counter = 1

        while True:
            try:
                if self.rc_ser.isOpen():
                    self.rc_ser.close()

                self.rc_ser.open()
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

    def send_data(self, message):
        """Method to send data to controller depending on system state
           Return nothing"""
        self.complete_quest += 1
        self.rc_ser.write(message+str(self.complete_quest)+'\n')

    def get_data(self):
        """Method to get data from rc controller
           Return getting data"""
        try:
            while self.rc_ser.inWaiting() > 0:
                data = self.rc_ser.read_until()

                return data

        except TimeoutError:

            pass
