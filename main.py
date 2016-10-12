
from serialConnection import SerialPort
from pyIbus import Ibus
import time
import threading
import pyIbus
current_milli_time = lambda: int(round(time.time() * 1000))
isPoolNeeded = True
phoneLed1="\xC8\x04\xF0\x2B\x54\x43"
yellowLed = "\xC8\x04\xF0\x2B\x32\x25"
phoneLed2= "\xC8\x04\xF0\x2B\x01\x16"

cdstart = "\x68\x12\x3b\x23\x62\x10\x43\x44\x43\x20\x31\x2d\x30\x34\x20\x20\x20\x20\x20\x4c"




def main():
    global ibusbuff
    global ibusPos
    print("Dziala!")
    ibusDev = Ibus() 

    timeNow = current_milli_time()
    lastTime = timeNow

    ibusDev.announceCallback()
    ibusDev.serialDev.write(phoneLed1)
    time.sleep(1)
    ibusDev.serialDev.write(phoneLed2)
    ibusDev.serialDev.flushInput()

    while True:
        ibusDev.receive()
                

if __name__ == "__main__":
    main()