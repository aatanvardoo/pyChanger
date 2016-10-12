#from serialConnection import SerialPort
import serialConnection
import time
import threading

#announcement message
announcementReq = "\x18\x04\xFF\x02\x01\xE0"
cdpoll = "\x68\x03\x18\x01\x72"
#info/status request
statReq = "\x68\x05\x18\x38\x00\x00\x4d"
radioPollReq = "\x18\x04\xFF\x02\x00\xE1"
startPlayResp= "\x18\x0a\x68\x39\x02\x09\x00\x01\x00\x01\x04\x4c"
stopPlayingReq = "\x68\x05\x18\x38\x01\x00\x4c"
stopPlayingResp= "\x18\x0a\x68\x39\x00\x02\x00\x01\x00\x01\x04\x45"
pausePlayingReq = "\x68\x05\x18\x38\x02\x00\x4f"
pasuePlayingResp = "\x18\x0a\x68\x39\x01\x0c\x00\x01\x00\x01\x04\x4a"
startPlayReq = "\x68\x05\x18\x38\x03\x00\x4e"
cdChangeReq = "\x68\x03\x18\x38\x06"
trackChangeReq = "\x68\x04\x18\x38\x0a\x4D"

cdPrevReq = "\x68\x05\x18\x38\x0a\x01\x46"
cdNextReq = "\x68\x05\x18\x38\x0a\x00\x47"

bmForwPush =[0xF0, 0x04, 0x68, 0x48, 0x00, 0xD4] 
bmForwRel = [0xF0, 0x04, 0x68, 0x48, 0x80, 0x54]
bmForwPress = [0xF0, 0x04, 0x68, 0x48, 0x40, 0x94]
yatourPoll= [255, 4, 255, 2, 0, 6]
ibusbuff=[]
ibusPos = 0
class Ibus(serialConnection.SerialPort):

    #Timer to announce CD every 25-30 s
    def announceCallback(self):
        print("Hey Im a CD changer! " + time.ctime())
        self.serialDev.write(announcementReq)
        threading.Timer(25, self.announceCallback).start()
    
    def checkSumCalculator(self, message, length):
        #print("Checksum calculator starts for", str(message) )
        
        suma = message[0]
        
        for i in range(1,length-1):
            suma = suma ^ (message[i]) #xor
            #print(hex(phoneLed[i]), hex(suma))
        
        if suma == (message[length-1]):
            #print( "Hurra checksum match")
            return True
        else:
            print( "Uuuu checksum failed",str(suma), str((message[length-1])), str(length))
            return False
        
    def receiveIbusMessages(self, bytesRead):
        global ibusPos
        global ibusbuff
        if bytesRead >= 4:
            length = ibusbuff[1]+2
            if  length == bytesRead:
                print("Only one message")
                if self.checkSumCalculator(ibusbuff[0:bytesRead], bytesRead):
                    #print('I read from ibus' + hexPrint(ibusbuff[0:bytesRead], bytesRead) + " length " + str(bytesRead))
                    
                    #handle message in corrrect way
                    self.handleIbusMessage(ibusbuff[0:bytesRead])
                    ibusbuff[0:bytesRead] = [] #cleaning arrays
                    ibusPos = ibusPos - bytesRead
                else:
                    print('I read from ibus ERROR'  + self.hexPrint(ibusbuff[0:bytesRead]) + " length " + str(bytesRead))
    
                    
            elif bytesRead > 8 :
                print("Possible more messages")
                msgLenIndx = 1 #starting from beggining message length should be stored on second index
                msgStartIdx = 0 #Message starts from very beggining
                for i in range(5):
                    print(msgLenIndx)
                    length = (ibusbuff[msgLenIndx]) + 2 #message length is saved on second index but whole message has two more fields
                    print("bytesread: " + str(bytesRead) + " length " + str(length) +  " i "+str(i))
                    if self.checkSumCalculator(ibusbuff[msgStartIdx:bytesRead],length):
                        #print('I read from ibus more than one ' + hexPrint(ibusbuff[msgStartIdx:bytesRead], length) + " length " + str(length -2))
                        
                        #handle message in corrrect way
                        self.handleIbusMessage(ibusbuff[msgStartIdx:msgStartIdx+length]) 
                        ibusbuff[msgStartIdx:msgStartIdx+length] = [] #cleaning arrays
                        ibusPos = ibusPos - length
                        if(msgLenIndx + length) >= bytesRead: # we dont want to look for more messages then received on serial bus
                            break
                        msgLenIndx = msgLenIndx+length #next message length field should be placeed in new meessage so aafter the first one
                        msgStartIdx = msgStartIdx + length #same here we moved to beggining of a next message
                    else: #if checksum fails there is no point to look for any other message
                        print("ERROR")
                        ibusbuff = [] #cleaning arrays
                        ibusPos = 0
                        return
                                
    def receive(self):
        global ibusPos
        global ibusbuff
        n = self.serialDev.inWaiting()
        if n != 0:

            out = self.serialDev.read(n)
            out = map(ord,out)
            ibusbuff.extend(out)
            ibusPos = ibusPos + n
            if ibusPos >= 64:
                ibusPos = 0
            #print("Received" + str(ibusbuff))        
            #if timeNow - lastTime > 5 :
            #    ibusPos = 0
            #    print "Timeout"
                
            #lastTime = timeNow
            self.receiveIbusMessages(ibusPos)
            
    def handleIbusMessage(self,message):
        prefix = "Got message: "
        print('I read from ibus' + self.hexPrint(message,len(message)) + " length: " + str(len(message)) )

        if message == cdpoll:
            print(prefix + "Radio poll req") 
            self.serialDev.write(radioPollReq)
            
        if message == yatourPoll:
            print(prefix + "Poll req") 
            self.serialDev.write(cdpoll)
        elif message == statReq:
            print(prefix + "staus/info request")
            self.serialDev.write(startPlayResp)   
            
        elif message == stopPlayingReq:
            print(prefix + "stop request") 
            self.serialDev.write(stopPlayingResp) 
            
        elif message == pausePlayingReq:  
            print(prefix + "pause request") 
            self.serialDev.write(pasuePlayingResp)
            
        elif message == startPlayReq:
            print(prefix + "start request") 
            self.serialDev.write(startPlayResp)
            
        elif message == cdChangeReq:
            print(prefix + "CD change request") 
            self.serialDev.write(startPlayResp)
            
        elif message == cdPrevReq:
            print(prefix + "CD previous request") 
            self.serialDev.write(startPlayResp)
           
        elif message == cdNextReq:
            print(prefix + "CD Next request") 
            self.serialDev.write(startPlayResp)    
            
        elif message == trackChangeReq:
            print(prefix + "Track change request") 
            self.serialDev.write(startPlayResp)
            
        elif message == bmForwPush:
            print("Got message from bmForwPush")
        elif message == bmForwRel:
            print("Got message from bmForwRel")
        elif message == bmForwPress:
            print("Got message from bmForwPress")
            
            
    def hexPrint(self, message, length):
        temp = [0 for i in range(length)]
        for i in range(length):
            temp[i]=hex((message[i]))
        return str(temp)