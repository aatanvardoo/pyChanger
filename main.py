from pyIbus import Ibus
import time

from kodijson import Kodi
from optparse import OptionParser

isPoolNeeded = True
phoneLed1=[0xC8,0x04,0xF0,0x2B,0x54,0x43]
phoneLedRed= [0xC8,0x04,0xF0,0x2B,0x01]
phoneLedGreen = [0xC8,0x04,0xF0,0x2B,0x10]
phoneLedYellow= [0xC8,0x04,0xF0,0x2B,0x04]



def main():

    parser = OptionParser()
    parser.add_option("-m", "--model", dest="model", help="set Your BMW model")
    (opts, args) = parser.parse_args()
    
    if opts.model is not None:
        print("Model: " + opts.model)
    
    if opts.model == "e39":
        time.sleep(40) #we are giving time to setup everything before python is up

    ibusDev = Ibus() 

    ibusDev.IbusSendTask()
    if opts.model == "e39-debug":
        ibusDev.announceCallback()


    ibusDev.initPlaylists()
    ibusDev.setPlaylist()
    ibusDev.playSong()
    
    ibusDev.sendToKodi()
    ibusDev.readKodi()
    
    ibusDev.sendIbusAndAddChecksum(phoneLedYellow)
    time.sleep(0.5)
    ibusDev.sendIbusAndAddChecksum(phoneLedRed)
    time.sleep(0.5)
    ibusDev.sendIbusAndAddChecksum(phoneLedGreen)
    ibusDev.clearInput()

    
     
    while True:
        ibusDev.receive()
                

if __name__ == "__main__":
    main()