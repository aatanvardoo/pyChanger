import serial
from serial.serialutil import SerialException
from kodijson import Kodi
import RPi.GPIO as GPIO

class SerialPort:
    channel = 17
    channel2 = 27
    kodi = Kodi("http://192.168.10.1:8080/jsonrpc", "kodi", "kodi")

    def __init__(self):
        print( self.kodi.JSONRPC.Ping())
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.channel, GPIO.IN)
        GPIO.setup(self.channel2, GPIO.OUT)
        GPIO.output(self.channel2, 0)
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
            

            
