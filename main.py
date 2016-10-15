
from serialConnection import SerialPort
from pyIbus import Ibus
import time
import threading
import pyIbus

isPoolNeeded = True
phoneLed1=[0xC8,0x04,0xF0,0x2B,0x54,0x43]
yellowLed = "\xC8\x04\xF0\x2B\x32\x25"
phoneLed2= [0xC8,0x04,0xF0,0x2B,0x01,0x16]

cdstart = "\x68\x12\x3b\x23\x62\x10\x43\x44\x43\x20\x31\x2d\x30\x34\x20\x20\x20\x20\x20\x4c"


def main():
    global ibusbuff
    global ibusPos
    print("Dziala!")
    ibusDev = Ibus() 

    ibusDev.announceCallback()
    ibusDev.sendIbus(phoneLed1)
    time.sleep(1)
    ibusDev.sendIbus(phoneLed2)
    ibusDev.serialDev.flushInput()

    while True:
        ibusDev.receive()
                

if __name__ == "__main__":
    main()