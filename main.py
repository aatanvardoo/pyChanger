
from serialConnection import SerialPort
import time

current_milli_time = lambda: int(round(time.time() * 1000))
phoneLed="\x80\x04\x3B\x11\x03\xAD"
cdstart = "\x68\x12\x3b\x23\x62\x10\x43\x44\x43\x20\x31\x2d\x30\x34\x20\x20\x20\x20\x20\x4c"
cdpoll = "\x68\x03\x18\x01\x72"
yatourPoll=[255, 4, 255, 2, 0, 6]
bmForwPush =[0xF0, 0x04, 0x68, 0x48, 0x00, 0xD4] 
bmForwRel = [0xF0, 0x04, 0x68, 0x48, 0x80, 0x54]
bmForwPress = [0xF0, 0x04, 0x68, 0x48, 0x40, 0x94]

def handleIbusMessage(message,ser):
    
    if message == yatourPoll:
        print("Got message from Yatour") 
        ser.serialDev.write(cdpoll)
        ser.serialDev.write(cdstart)
        
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
        print( "Uuuu checksum failed",str(suma), str(message[length]), str(length))
        return False
        
ibusbuff=[0 for i in range(64)]
ibusPos = 0
def main():
    global ibusbuff
    global ibusPos
    print("Dziala!")
    
    serialP = SerialPort()
    timeNow = current_milli_time()
    lastTime = timeNow
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
                    print('I read from ibus ERROR'  + str(ibusbuff[0:ibusPos]) + " length " + str(ibusPos))
                ibusPos = 0

if __name__ == "__main__":
    main()