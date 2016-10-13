from serialConnection import SerialPort
import serialConnection
import time
import threading

#test
statReqTest =          "\x68\x05\x18\x38\x00\x00\x4d"
cdpollTest =           "\x68\x03\x18\x01\x72"
stopPlayingReqTest =   "\x68\x05\x18\x38\x01\x00\x4c"
pausePlayingReqTest =  "\x68\x05\x18\x38\x02\x00\x4f"
startPlayReqTest    =  "\x68\x05\x18\x38\x03\x00\x4e"
cdChangeReqTest =      "\x68\x05\x18\x38\x06\x01\x4a"
cdPrevReqTest =        "\x68\x05\x18\x38\x0a\x01\x46"
cdNextReqTest =        "\x68\x05\x18\x38\x0a\x00\x47"
trackChangeReqTest =   "\x68\x04\x18\x38\x0a\x4D" #weryfy if that is neccesarryyyy!!!!!!!!!!!!
bmForwPushTest =       "\xF0\x04\x68\x48\x00\xD4" 
bmForwRelTest =        "\xF0\x04\x68\x48\x80\x54"
bmForwPress =          "\xF0\x04\x68\x48\x40\x94"

trackChangeNextReqTest = "\x68\x05\x18\x38\x0a\x00\x47" #Changes track/song to next
trackChangePrevReqTest = "\x68\x05\x18\x38\x0a\x01\x46" #Changes track/song to next

testMessages = [cdChangeReqTest, trackChangePrevReqTest]
#announcement message
announcementReq = [0x18,0x04,0xFF,0x02,0x01,0xE0]

#info/status request

radioPollReq = [0x18,0x04,0xFF,0x02,0x00,0xE1]
startPlayResp= "\x18\x0a\x68\x39\x02\x09\x00\x01\x00\x01\x04\x4c"
stopPlayingReq = [0x68,0x05,0x18,0x38,0x01,0x00,0x4c]
stopPlayingResp= "\x18\x0a\x68\x39\x00\x02\x00\x01\x00\x01\x04\x45"
pausePlayingReq = [0x68,0x05,0x18,0x38,0x02,0x00,0x4f]
pasuePlayingResp = "\x18\x0a\x68\x39\x01\x0c\x00\x01\x00\x01\x04\x4a"
startPlayReq =   [0x68,0x05,0x18,0x38,0x03,0x00,0x4e]
cdChangeReq =    [0x68, 0x05, 0x18, 0x38, 0x06, 0xFF, 0xff]
trackChangeNextReq = [0x68,0x05,0x18,0x38,0x0a,0x00,0x47] #Changes track/song to next
trackChangePrevReq = [0x68,0x05,0x18,0x38,0x0a,0x01,0x46] #Changes track/song to next
endPlayingResp =  "\x18\x0a\x68\x39\x01\x0c\x00\x01\x00\x01\x04\x4a"

statReq =     [0x68,0x05,0x18,0x38,0x00,0x00,0x4d]
cdpoll =      [0x68,0x03,0x18,0x01,0x72]
bmForwPush =  [0xF0, 0x04, 0x68, 0x48, 0x00, 0xD4] 
bmForwRel =   [0xF0, 0x04, 0x68, 0x48, 0x80, 0x54]
bmForwPress = [0xF0, 0x04, 0x68, 0x48, 0x40, 0x94]
yatourPoll=   [255, 4, 255, 2, 0, 6]
ibusbuff=[]
ibusPos = 0
class Ibus(serialConnection.SerialPort):
    cdNumber = 0
    #Timer to announce CD every 25-30 s
    def announceCallback(self):
        print("Hey Im a CD changer! " + time.ctime())
        self.sendIbus(announcementReq)
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
            print( "Uuuu checksum failed " + "calculated: " + str(hex(suma)) + " expected " + str(hex(message[length-1])) + " length " + str(length))
            return False
    def sendIbus(self,message):
        if hasattr(self, 'serialDev'):  
            self.serialDev.write(bytes(message)) 
        else:
            print("Serial in NOT opened " + self.serialName)
    def receiveIbusMessages(self, bytesRead):
        global ibusPos
        global ibusbuff
        if bytesRead >= 4:
            length = ibusbuff[1]+2
            if  length == bytesRead:
                print("Only one message")
                if self.checkSumCalculator(ibusbuff[0:bytesRead], bytesRead):
                    print('I read from ibus' + self.hexPrint(ibusbuff[0:bytesRead], bytesRead) + " length " + str(bytesRead))
                    
                    #handle message in corrrect way
                    self.handleIbusMessage(ibusbuff[0:bytesRead])
                    ibusbuff[0:bytesRead] = [] #cleaning arrays
                    ibusPos = ibusPos - bytesRead
                else:
                    print('I read from ibus ERROR'  + self.hexPrint(ibusbuff[0:bytesRead],bytesRead) + " length " + str(bytesRead))
    
                    
            elif bytesRead > 8 :
                print("Possible more messages")
                msgLenIndx = 1 #starting from beggining message length should be stored on second index
                msgStartIdx = 0 #Message starts from very beggining
                for i in range(5):
                    print(msgLenIndx)
                    length = (ibusbuff[msgLenIndx]) + 2 #message length is saved on second index but whole message has two more fields
                    print(self.hexPrint(ibusbuff, len(ibusbuff) ) + "bytesread: " + str(bytesRead) + " length " + str(length) +  " i "+str(i))
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
            #out = map(ord,out)
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
        print('I read from ibus' + self.hexPrint(message,len(message)) + " length: " + str(len(message)) + "    ", end="" )

        if message == cdpoll:
            print(prefix + "Radio poll req") 
            self.sendIbus(radioPollReq)
            
        if message == yatourPoll:
            print(prefix + "Poll req") 
            self.sendIbus(cdpoll)
            
        elif message == statReq:
            print(prefix + "staus/info request")
            self.sendIbus(startPlayResp)
            
        elif message == stopPlayingReq:
            print(prefix + "stop request") 
            self.sendIbus(stopPlayingResp) 
            
        elif message == pausePlayingReq:  
            print(prefix + "pause request") 
            self.sendIbus(pasuePlayingResp)
            
        elif message == startPlayReq:
            print(prefix + "start request") 
            self.sendIbus(startPlayResp)
            
            #here some of message prameters may vary so only static part is compared
        elif message[0:5] == cdChangeReq[0:5]:
            #extracting parameters
            self.cdNumber = message[5]
            print(prefix + "CD change request. Cd to load: " + str(self.cdNumber) ) 
                #cdstatus = CD_STATUS_END_PLAYING;
                #send_cdstatus();
                #cdstatus = CD_STATUS_PLAYING;
                #send_cdstatus();
            self.sendIbus(startPlayResp)
            
        elif message == trackChangePrevReq:
            print(prefix + "Track previous request") 
            self.sendIbus(startPlayResp)
           
        elif message == trackChangeNextReq:
            print(prefix + "Track next request") 
            self.sendIbus(startPlayResp)    
            
         
           
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
    
    
    
    def receiveTest(self):
        global ibusPos
        global ibusbuff
        n = 1
        if n != 0:
            for msg in range(len(testMessages)):
                for i in range(0,len(testMessages[msg]),n):
                    out = testMessages[msg][i]
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
                
                
                
import unittest

class IbusUt(unittest.TestCase):
    def test_uno(self):
        print("Im a test")
    
    
    
if __name__ == "__main__":
    unittest.main(verbosity=2)