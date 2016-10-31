import serial
from serial.serialutil import SerialException

class SerialPort:

    def __init__(self):

        try:
            print("Trying to open USB")
            self.serialName = '/dev/ttyUSB0'
            self.serialDev = serial.Serial(
                           port=self.serialName,
                           baudrate=9600, 
                           parity=serial.PARITY_EVEN, 
                           stopbits=serial.STOPBITS_ONE,
                           bytesize=serial.EIGHTBITS,
                           timeout = None,
                           xonxoff = False,
                           rtscts = False,
                           dsrdtr = False
                           
                           )
        except SerialException as e:
            print (e)
            

            
