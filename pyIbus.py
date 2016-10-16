from serialConnection import SerialPort
import serialConnection
import time
import threading
import uinput
#test
yatourPollTest =       "\xff\x04\xff\x02\x00\x06"
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
current_sec_time = lambda: int(round(time.time()))
current_milli_time = lambda: int(round(time.time() * 1000))
trackChangeNextReqTest = "\x68\x05\x18\x38\x0a\x00\x47" #Changes track/song to next
trackChangePrevReqTest = "\x68\x05\x18\x38\x0a\x01\x46" #Changes track/song to next

brakemsgReqTest =      "\x63\x10\x18\x38\x03\x01\x4a"
randomModeReqTest =    "\x68\x05\x18\x38\x08\x01\x44"
introModeReqTest =    "\x68\x05\x18\x38\x07\x01\x4b"

scanTrackReqForwTest = "\x68\x05\x18\x38\x04\x00\x49"
scanTrackReqBckTest =  "\x68\x05\x18\x38\x04\x01\x48"
testMessages = scanTrackReqForwTest + bmForwPress + statReqTest+ scanTrackReqForwTest +scanTrackReqForwTest + statReqTest+ scanTrackReqForwTest+ scanTrackReqForwTest+scanTrackReqForwTest
#announcement message
announcementReq = [0x18,0x04,0xFF,0x02,0x01,0xE0]

#info/status request

radioPollResp = [0x18,0x04,0xFF,0x02,0x00,0xE1]
startPlayResp= [0x18,0x0a,0x68,0x39,0x02,0x09,0x00,0x01,0x00,0x01,0x04,0x4c]
stopPlayingReq =  [0x68,0x05,0x18,0x38,0x01,0x00,0x4c]
stopPlayingResp= "\x18\x0a\x68\x39\x00\x02\x00\x01\x00\x01\x04\x45"
pausePlayingReq = [0x68,0x05,0x18,0x38,0x02,0x00,0x4f]
pasuePlayingResp = "\x18\x0a\x68\x39\x01\x0c\x00\x01\x00\x01\x04\x4a"
startPlayReq =    [0x68,0x05,0x18,0x38,0x03,0x00,0x4e]
cdChangeReq =     [0x68, 0x05, 0x18, 0x38, 0x06, 0xFF, 0xff]
trackChangeNextReq = [0x68,0x05,0x18,0x38,0x0a,0x00,0x47] #Changes track/song to next
trackChangePrevReq = [0x68,0x05,0x18,0x38,0x0a,0x01,0x46] #Changes track/song to next
endPlayingResp =  "\x18\x0a\x68\x39\x01\x0c\x00\x01\x00\x01\x04\x4a"

randomModeReq = [0x68, 0x5, 0x18, 0x38, 0x08, 0xFF, 0xFF]
introModeReq =  [0x68, 0x5, 0x18, 0x38, 0x07, 0xFF, 0xFF]

scanTrackReq = [0x68, 0x05, 0x18, 0x38, 0x04, 0xFF, 0xFF]
statReq =      [0x68, 0x05, 0x18,  0x38,0x00,0x00,0x4d]
cdpoll =       [0x68, 0x03, 0x18,  0x01,0x72]
bmForwPush =   [0xF0, 0x04, 0x68, 0x48, 0x00, 0xD4] 
bmForwRel =    [0xF0, 0x04, 0x68, 0x48, 0x80, 0x54]
bmForwPress =  [0xF0, 0x04, 0x68, 0x48, 0x40, 0x94]
yatourPoll=    [255, 4, 255, 2, 0, 6]
ibusbuff=[]
ibusPos = 0

CD_STATUS_NOT_PLAYING = [0x00, 0x02]
CD_STATUS_NO_MAGAZINE = [0x0a, 0x02]
CD_STATUS_LOADING     = [0x09, 0x02]
CD_STATUS_SEEKING     = [0x08, 0x02]
CD_STATUS_PAUSE       = [0x01, 0x0c]
CD_STATUS_PLAYING     = [0x02, 0x09]
CD_STATUS_END_PLAYING = [0x07, 0x02]
CD_STATUS_SCAN_FORWARD =  [0x03, 0x09]
CD_STATUS_SCAN_BACKWARD = [0x04, 0x09]

header1 = [0x68, 0x05, 0x18]
header2 = [0x68, 0x04, 0x18]
header3 = [0x68, 0x03, 0x18]
header4 = [0xF0, 0x04, 0x68]
class Ibus(serialConnection.SerialPort):
    cdNumber = 1
    trackNumber = 1
    isAnnouncementNeeded = False
    cdStatus = CD_STATUS_LOADING
    random = False
    intro = 0
    lastTime = current_milli_time()
    def sendStatus(self):
        #compose status response
        message = [0x18,0x0a,0x68,0x39]
        #is random mode on/off
        if self.random:
            self.cdStatus[1] = self.cdStatus[1] | 0x20 
        
        #is intro mode on off
        if self.intro:
            self.cdStatus[1] = self.cdStatus[1] | 0x10     
        #compose message    
        message = message + self.cdStatus + [0x00, 0x3F, 0x00] + [self.cdNumber, self.trackNumber] 
        checksum = self.checkSumInject(message, len(message))
        #add checksum at the end
        message = message + [checksum]
        print("Send status: " + self.hexPrint(message, len(message)))
        self.sendIbus(message)
        
        
    #Timer to announce CD every 25-30 s
    def announceCallback(self):
        if self.isAnnouncementNeeded:
            self.sendIbus(announcementReq)
            threading.Timer(25, self.announceCallback).start()
    
    def checkSumCalculator(self, message, length):
        
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
        
    def checkSumInject(self, message, length):
        
        suma = message[0]
        for i in range(1,length):
            suma = suma ^ (message[i]) #xor
            #print(hex(message[i]), hex(suma))
        return suma
    
    def sendIbus(self,message):
        if hasattr(self, 'serialDev'):  
            self.serialDev.write(bytes(message)) 
        else:
            print("Serial in NOT opened " + self.serialName)
    
    def sendIbusAndAddChecksum(self,message):
        if hasattr(self, 'serialDev'):  
            checksum = self.checkSumInject(message, len(message))
            #add checksum at the end
            message = message + [checksum]
            self.serialDev.write(bytes(message)) 
        else:
            print("Serial in NOT opened " + self.serialName)
            
            
    def handleIbusMessage(self,message):
        prefix = "Last handled msg: "
      
        if message == cdpoll:
            prefix = prefix + "Radio poll req"
            self.isAnnouncementNeeded = False
            self.sendIbus(radioPollResp)
            
        if message == yatourPoll:
            prefix = prefix + "Poll req"
            self.sendIbus(cdpoll)
            
        elif message == statReq:
            prefix = prefix + "staus/info request"
            self.sendStatus()
            #self.sendIbus(startPlayResp)
        elif message == stopPlayingReq:
            prefix = prefix + "stop play request"
            self.cdStatus = CD_STATUS_NOT_PLAYING
            self.sendStatus()
            
        elif message == pausePlayingReq:  
            prefix = prefix + "pause play request"
            self.cdStatus = CD_STATUS_PAUSE
            self.sendStatus()
            
        elif message == startPlayReq:
            prefix =prefix + "start play request"
            self.cdStatus = CD_STATUS_PLAYING
            self.sendStatus()
            
            #here some of message prameters may vary so only static part is compared
        elif message[0:5] == cdChangeReq[0:5]:
            #extracting parameters
            self.cdNumber = message[5]
            prefix = prefix + "CD change request. Cd to load: " + str(self.cdNumber)
                
            self.cdStatus = CD_STATUS_END_PLAYING;
            self.sendStatus()    
            self.cdStatus = CD_STATUS_PLAYING;
            self.sendStatus() 
            
        elif message == trackChangePrevReq:
            self.trackNumber = (self.trackNumber - 1) % 60
            prefix = prefix + "Track previous request. Track: " + str(self.trackNumber)
            self.cdStatus = CD_STATUS_END_PLAYING;
            self.sendStatus()    
            self.cdStatus = CD_STATUS_PLAYING;
            self.sendStatus() 
           
        elif message == trackChangeNextReq:
            self.trackNumber = (self.trackNumber + 1) % 60
            prefix = prefix + "Track next request. Track: " + str(self.trackNumber)
            self.cdStatus = CD_STATUS_END_PLAYING;
            self.sendStatus()    
            self.cdStatus = CD_STATUS_PLAYING;
            self.sendStatus()               
         
        elif message[0:5] == randomModeReq[0:5]:
            
            if message[5] == 0x01:
                
                self.random = True
            else:
                self.random = False
        
            prefix = prefix + "Random mode: " + str(self.random)    
            self.sendStatus()    
        
        elif message[0:5] == introModeReq[0:5]:
            
            if message[5] == 0x01:
                
                self.intro = True
            else:
                self.intro = False
        
            prefix = prefix + "Intro mode: " + str(self.random)    
            self.sendStatus()        
           
        elif message[0:5] == scanTrackReq[0:5]:
            
            if self.cdStatus == CD_STATUS_PLAYING:
                #no scan if music is not playing
                if message[5] == 0x00:
                    self.cdStatus = CD_STATUS_SCAN_FORWARD
                else:
                    self.cdStatus = CD_STATUS_SCAN_BACKWARD
                    
            prefix = prefix + "Scanning. It is not HANDLED"
            #is this really needed?     
            #self.sendStatus()    

        elif message == bmForwPush:
            print("Got message from bmForwPush")
        elif message == bmForwRel:
            print("Got message from bmForwRel")
        elif message == bmForwPress:
            print("Got message from bmForwPress")
        
        time = current_sec_time()    
        print(str(time)+ "   " + prefix + '  ' + self.hexPrint(message,len(message)) + " length: " + str(len(message)) )   
            
    def hexPrint(self, message, length):
        temp = [0 for i in range(length)]
        for i in range(length):
            temp[i]=hex((message[i]))
        return str(temp)
    
    def receiveIbusMessages(self, bytesRead):
        global ibusPos
        global ibusbuff
        if ibusPos >= 7:
            #Im interested only in messages to CD changer. With three length variants: 3,4,5
            if ibusbuff[0:3] == header1 or ibusbuff[0:3] == header2 or ibusbuff[0:3] == header3 or ibusbuff[0:3] == header4:
                print("Got message to CD changer")
                lenght = ibusbuff[1]+2
                #if self.checkSumCalculator(ibusbuff[0:lenght], lenght): #do we really need this now?
                self.handleIbusMessage(ibusbuff[0:lenght])
                    #removing message as it was handled
                ibusbuff[0:lenght] = []
                ibusPos = len(ibusbuff)

            else:
                #shift left
                print("Cutting")
                ibusbuff[0:bytesRead] = []
                ibusPos = ibusPos - bytesRead 
    
    def receiveTest(self):
        global ibusPos
        global ibusbuff
        n = 1
        if n != 0:
            for i in range(0,len(testMessages),n):
                out = testMessages[i]
                out = map(ord,out)
                ibusbuff.extend(out)
                ibusPos = ibusPos + n
                if ibusPos >= 64:
                    ibusPos = 0
                    ibusbuff = []
                
                self.receiveIbusMessages(n)
                print("Received " +str(ibusPos) + "  " + self.hexPrint(ibusbuff, len(ibusbuff))) 
                
                
    def receiveOpt(self):
        global ibusPos
        global ibusbuff


        out = self.serialDev.read(3)
        if out:
            ibusbuff.extend(out)
            ibusPos = ibusPos + 3
            if ibusPos >= 64:
                ibusPos = 0
                ibusbuff = []
            self.receiveIbusMessages(3)
        else:
            time.sleep(0.01)
            #print("Received " +str(ibusPos) + "  " + self.hexPrint(ibusbuff, len(ibusbuff)))   
                
                
                
import unittest

class IbusUt(unittest.TestCase):
    def test_uno(self):
        print("Im a test")
    
    
    
if __name__ == "__main__":
    unittest.main(verbosity=2)