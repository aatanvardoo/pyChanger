
from serialConnection import SerialPort
import time
import threading

current_milli_time = lambda: int(round(time.time() * 1000))
isPoolNeeded = True
phoneLed1="\xC8\x04\xF0\x2B\x54\x43"
phoneLed2= "\xC8\x04\xF0\x2B\x01\x16"

cdstart = "\x68\x12\x3b\x23\x62\x10\x43\x44\x43\x20\x31\x2d\x30\x34\x20\x20\x20\x20\x20\x4c"
cdpoll = [0x68,0x03,0x18,0x01,0x72]
cdpollTest = "\x68\x03\x18\x01\x72"
yatourPoll=[255, 4, 255, 2, 0, 6]
bmForwPush =[0xF0, 0x04, 0x68, 0x48, 0x00, 0xD4] 
bmForwRel = [0xF0, 0x04, 0x68, 0x48, 0x80, 0x54]
bmForwPress = [0xF0, 0x04, 0x68, 0x48, 0x40, 0x94]

#info/status request
statReq = [0x68,0x05,0x18,0x38,0x00,0x00,0x4d]

#announcement message
announcementReq = "\x18\x04\xFF\x02\x01\xE0"

radioPollReq = "\x18\x04\xFF\x02\x00\xE1"

stopPlayingReq = [0x68,0x05,0x18,0x38,0x01,0x00,0x4c]
stopPlayingResp= "\x18\x0a\x68\x39\x00\x02\x00\x01\x00\x01\x04\x45"

pausePlayingReq = [0x68,0x05,0x18,0x38,0x02,0x00,0x4f]
pasuePlayingResp = "\x18\x0a\x68\x39\x01\x0c\x00\x01\x00\x01\x04\x4a"

startPlayReq = [0x68,0x05,0x18,0x38,0x03,0x00,0x4e]
startPlayResp= "\x18\x0a\x68\x39\x02\x09\x00\x01\x00\x01\x04\x4c"

cdChangeReq = [0x68,0x03,0x18,0x38,0x06]

trackChangeReq = [0x68,0x04,0x18,0x38,0x0a,0x4D]
trackChangeReqtemp = [0x68,0x04, 0x18, 0x38, 0x0a, 0x4D]
#def handleStatusReq(ser):
    #lest assum it is always playing
    #to be done play or no...
    

    
def handleIbusMessage(message,ser):
    global isPoolNeeded
    prefix = "Got message: "
    
    #if message == yatourPoll:
    #    print(prefix + "Poll req") 
    #    ser.serialDev.write(cdpoll)
    
    if message == cdpoll:
        isPoolNeeded = False
        print(prefix + "Radio poll req") 
        ser.serialDev.write(radioPollReq)
        
    elif message == statReq:
        print(prefix + "staus/info request")
        ser.serialDev.write(startPlayResp)   
        
    elif message == stopPlayingReq:
        print(prefix + "stop request") 
        ser.serialDev.write(stopPlayingResp) 
        
    elif message == pausePlayingReq:  
        print(prefix + "pause request") 
        ser.serialDev.write(pasuePlayingResp)
        
    elif message == startPlayReq:
        print(prefix + "start request") 
        ser.serialDev.write(startPlayResp)
        
    elif message == cdChangeReq:
        print(prefix + "CD change request") 
        ser.serialDev.write(startPlayResp)
        
    elif message == trackChangeReq:
        print(prefix + "Track change request") 
        ser.serialDev.write(startPlayResp)
        
    elif message == bmForwPush:
        print("Got message from bmForwPush")
    elif message == bmForwRel:
        print("Got message from bmForwRel")
    elif message == bmForwPress:
        print("Got message from bmForwPress")
    
def hexPrit(message, length):
    temp = [0 for i in range(length)]
    for i in range(length):
        temp[i]=hex(message[i])
    return str(temp)

#Timer to announce CD every 25-30 s
def announceCallback():
    global isPoolNeeded
    if isPoolNeeded == True:
        print("Hey Im a CD changer! " + time.ctime())
        serialP.serialDev.write(announcementReq)
    threading.Timer(25, announceCallback).start()

def checkSumCalculator(message, length):
    #print("Checksum calculator starts for", str(message) )
    
    suma = message[0]
    
    for i in range(1,length-1):
        suma = suma ^ message[i] #xor
        #print(hex(phoneLed[i]), hex(suma))
    
    if suma == message[length-1]:
        #print( "Hurra checksum match")
        return True
    else:
        print (str(length))
        print( "Uuuu checksum failed",str(suma), str(message[length-1]), str(length))
        return False
        
ibusbuff=[0 for i in range(64)]
ibusPos = 0
serialP = SerialPort()
def main():
    global ibusbuff
    global ibusPos
    print("Dziala!")
    

    timeNow = current_milli_time()
    lastTime = timeNow
    cdpoll


    serialP.serialDev.write(phoneLed1)
    time.sleep(1)
    serialP.serialDev.write(phoneLed2)
    serialP.serialDev.flushInput()
    announceCallback();
    

    while True:
        n = serialP.serialDev.inWaiting()
        if n != 0:

            out = serialP.serialDev.read(n)
            for i in range(n): #sometimes red retunrns more than one hex string
                # print str(n) +" " +  str(ibusPos)
                ibusbuff[ibusPos] = ord(out[i])
                ibusPos = ibusPos + 1
                if ibusPos >= 64:
                    ibusPos = 0
            #print("Received" + str(ibusbuff))        
            if timeNow - lastTime > 5 :
                ibusPos = 0
                print "Timeout"
                
            lastTime = timeNow

                
            if ibusPos >=4 and ibusbuff[1]+2 == ibusPos:
                if checkSumCalculator(ibusbuff[0:ibusPos], ibusPos):
                    print('I read from ibus' + hexPrit(ibusbuff[0:ibusPos], ibusPos) + " length " + str(ibusPos))
                    
                    handleIbusMessage(ibusbuff[0:ibusPos],serialP)
                else:
                    print('I read from ibus ERROR'  + hexPrit(ibusbuff[0:ibusPos],ibusPos) + " length " + str(ibusPos))
                ibusPos = 0

if __name__ == "__main__":
    main()