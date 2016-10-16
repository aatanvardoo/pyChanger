import uinput
from serialConnection import SerialPort
from pyIbus import Ibus
import time
import threading
import pyIbus

isPoolNeeded = True
phoneLed1=[0xC8,0x04,0xF0,0x2B,0x54,0x43]
phoneLedRed= [0xC8,0x04,0xF0,0x2B,0x01]
phoneLedGreen = [0xC8,0x04,0xF0,0x2B,0x10]
phoneLedYellow= [0xC8,0x04,0xF0,0x2B,0x04]
status = [0x68, 0x5, 0x18, 0x38, 0x0, 0x0, 0x4d]
# Define a function for the thread
def print_time():

    while True:
        time.sleep(0.005)
        #print("OK")
        ibusDev.sendIbus(phoneLed1)

def stat():
    while True:
        time.sleep(5)
        #print("OK")
        ibusDev.sendIbus(status)
ibusDev = Ibus() 
def main():
    global ibusbuff
    global ibusPos
    print("Dziala!")


    ibusDev.sendIbusAndAddChecksum(phoneLedYellow)
    time.sleep(0.5)
    ibusDev.sendIbusAndAddChecksum(phoneLedRed)
    time.sleep(0.5)
    ibusDev.sendIbusAndAddChecksum(phoneLedGreen)
    ibusDev.serialDev.flushInput()
    
    #t = threading.Thread(target=print_time)

    #t.start()
    
    t = threading.Thread(target=stat)

    t.start()
    #ibusDev.announceCallback()
    #device = uinput.Device([
#        uinput.KEY_COMMA,

 #       uinput.KEY_DOT
  #      ])

    #device.emit_click(uinput.KEY_DOT)

    while True:
        ibusDev.receiveOpt()
                

if __name__ == "__main__":
    main()