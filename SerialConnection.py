#  Created by Antropov N.A. 12.11.19
import serial
from serial.tools import list_ports
import time
import struct


class SerialConnection:
    """Provide work with arduino serial port

       :param baudrate: connection rate (the default is 9600)
       :param device_name: device name in string
       :param device_id: device id in string
    """
    
    def __init__(self, baudrate=9600, device_name, device_id):
        
        self.device_name = device_name # Device name
        self.port = self.__portFind(device_id)  # Get port name
        self.baudrate = baudrate
        self.ser = serial.Serial(port=self.port, baudrate=self.baudrate)  # Serial port init
        self.__initSer()  # Serial connection open

    def __portFind(self, device_id):
        """Find port name
            
           Return port name
        """

        try:
            ports = list_ports.comports()

            for port, desc, hwid in sorted(ports):
                
                if hwid.find(device_id) != -1:
                   device_port = port

            print(self.device_name+" port name is ", device_port, "\n")
            return device_port
        
        except NameError:
            
            print("No connection betweeen "+self.device_name+" arduino and raspberry\n")

    def __initSer(self):
        """Method to init serial connection"""

        try_counter = 1
        
        while True:
            try:
                if self.ser.isOpen():

                    self.ser.close()

                self.ser.open()
                time.sleep(5)
                print(self.device_name+" serial port is availble. Connection is ready\n")
                break

            except (OSError, serial.SerialException):

                print(self.device_name+" port opening error. Try again\n")
                try_counter += 1

                if try_counter == 10:

                    print(self.device_name+" port is unavailable\n")
                    break

                else:
                    continue

    def sendData(self, msg, flag=False):
        """Send data to device depending on system state

           :param msg: message to send in bytes
           :param flag: flag of data type (the default is False)
        """

        try:
            #  Message structure: pi address + message + new line flag
            if flag:
                d1 = int(msg*100)

                s = d1 // 100
                d = (d1 - s*100) // 10
                e = d1 - s*100 - d*10

                s1 = str(s)
                d1 = str(d)
                e1 = str(e)

                s2 = bytes(s1, 'utf8')
                d2 = bytes(d1, 'utf8')
                e2 = bytes(e1, 'utf8')
                
                self.ser.write(struct.pack('4s3ss', b'1053',  s2+d2+e2, b'\n'))
            
            else:
            
                self.ser.write(b'105'+msg+b'\n')
                print("Message was sent: "+str(msg))
                time.sleep(1)

        except (OSError, serial.SerialException):

            print("Message Send Error")

    def getData(self):
        """Method to get data from device
        
            
           Return data or None string in bytes
        """

        try:

            while self.ser.inWaiting() > 0:

                data = self.ser.read_until()
                print("Message was received: "+str(data))
                return data

            return b'None'

        except (OSError, serial.SerialException):

            print("Message Get Error")
            return b'None'

    def getResponse(self):
        """Method to get response from device about message
        
           Return true if response was received else false
        """

        data = self.getData()

        if b'OK' in data:
            print("Response was received from device")
            return True

        return False
