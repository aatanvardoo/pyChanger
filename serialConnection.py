import serial
from serial.serialutil import SerialException
import time

class SerialPort:
    def __init__(self):
        try:
            self.serialName = '/dev/ttyUSB0'
            self.serialDev = serial.Serial(
                           port=self.serialName,
                           baudrate=9600, 
                           parity=serial.PARITY_EVEN, 
                           stopbits=serial.STOPBITS_ONE,
                           bytesize=serial.EIGHTBITS,
                           timeout = 1,
                           xonxoff = False,
                           rtscts = False,
                           dsrdtr = False,
                           writeTimeout = 2)
        except SerialException as e:
            print str(e)
            
    def receiveWithTimout(self,timeout = 3):
        timeout = time.time() + timeout #3sec timeout
        while 1:
            n = self.serialDev.inWaiting()
            if n != 0:
                out = self.serialDev.read(n)
                debug.DebugPrint('I read '  + out.encode("hex") + " length " + str(n))
                return out
            if time.time() > timeout:
                print "Timeout"
                break
            
        
        
class SerialPortTH(SerialPort):
    def readTH(self, bytearr):
        bytearr = bytearray(bytearr)
        tempr = bytearr[3]<<8 | bytearr[2]
        tempr = tempr / 10.0
    
        humidity = bytearr[5]<<8 | bytearr[4];
        humidity = humidity /10.0
        
        return {'humidity':humidity, 'tempr':tempr}
    
    def readAllAtOnce(self):
        if hasattr(self, 'serialDev'):
            if(self.serialDev.isOpen() == True):
                debug.DebugPrint(("Serial opened " + self.serialName))
                self.serialDev.write('ABAA'.decode('hex'))
                out = self.receiveWithTimout()
                ret = self.readTH(out)
                debug.DebugPrint(str(ret['humidity']) + " " + str(ret['tempr']))
                
                return {'humidity':ret['humidity'], 'tempr':ret['tempr']}