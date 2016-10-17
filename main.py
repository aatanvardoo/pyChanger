import uinput
from serialConnection import SerialPort
from pyIbus import Ibus
import time
import threading
import pyIbus
from pykeyboard import PyKeyboard

isPoolNeeded = True
phoneLed1=[0xC8,0x04,0xF0,0x2B,0x54,0x43]
phoneLedRed= [0xC8,0x04,0xF0,0x2B,0x01]
phoneLedGreen = [0xC8,0x04,0xF0,0x2B,0x10]
phoneLedYellow= [0xC8,0x04,0xF0,0x2B,0x04]



def main():

    print("Dziala!")
    ibusDev = Ibus() 

    ibusDev.sendIbusAndAddChecksum(phoneLedYellow)
    time.sleep(0.5)
    ibusDev.sendIbusAndAddChecksum(phoneLedRed)
    time.sleep(0.5)
    ibusDev.sendIbusAndAddChecksum(phoneLedGreen)
    ibusDev.serialDev.flushInput()
    #ibusDev.announceCallback()

    while True:
        ibusDev.receive()
                

if __name__ == "__main__":
    main()