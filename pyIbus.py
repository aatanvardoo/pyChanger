
import serialConnection
import time
import threading
from kodijson import Kodi

current_sec_time = lambda: int(round(time.time()))
current_milli_time = lambda: int(round(time.time() * 1000))

#announcement message
announcementReq = [0x18,0x04,0xFF,0x02,0x01,0xE0]

#info/status request

radioPollResp = [0x18,0x04,0xFF,0x02,0x00,0xE1]
startPlayResp= [0x18,0x0a,0x68,0x39,0x02,0x09,0x00,0x01,0x00,0x01,0x04,0x4c]
stopPlayingReq =  [0x68,0x05,0x18,0x38,0x01,0x00,0x4c]

pausePlayingReq = [0x68,0x05,0x18,0x38,0x02,0x00,0x4f]

startPlayReq =    [0x68,0x05,0x18,0x38,0x03,0x00,0x4e]
cdChangeReq =     [0x68, 0x05, 0x18, 0x38, 0x06, 0x01, 0x4a]
trackChangeNextReq = [0x68,0x05,0x18,0x38,0x0a,0x00,0x47] #Changes track/song to next
trackChangePrevReq = [0x68,0x05,0x18,0x38,0x0a,0x01,0x46] #Changes track/song to next


randomModeReq = [0x68, 0x5, 0x18, 0x38, 0x08, 0x01, 0x44]
introModeReq =  [0x68, 0x5, 0x18, 0x38, 0x07, 0x01, 0x4b]

scanTrackReq = [0x68, 0x05, 0x18, 0x38, 0x04, 0x01,0x48]
statReq =      [0x68, 0x05, 0x18,  0x38,0x00,0x00,0x4d]
cdpoll =       [0x68, 0x03, 0x18,  0x01, 0x72]
bmForwPush =   [0xF0, 0x04, 0x68, 0x48, 0x00, 0xD4] 
bmForwRel =    [0xF0, 0x04, 0x68, 0x48, 0x80, 0x54]
bmForwPress =  [0xF0, 0x04, 0x68, 0x48, 0x40, 0x94]
yatourPoll=    [255, 4, 255, 2, 0, 6]

ibusbuff=[0 for i in range(64)]
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
header5 = [255, 4, 255]

yatourPoll2=    [255, 0, 255, 2, 0]
stopPlayingReq2 =  [0x68,0x00,0x18,0x38,0x01,0x00]
pausePlayingReq2 = [0x68,0x00,0x18,0x38,0x02,0x00]
statReq2 =         [0x68,0x00,0x18,0x38,0x00,0x00]
trackChangeNextReq2 = [0x68,0x00,0x18,0x38,0x0a,0x00]
trackChangePrevReq2 = [0x68,0x05,0x18,0x38,0x0a,0x01]

randomModeReq2 = [0x68, 0x0, 0x18, 0x38, 0x08]

introModeReq2 =  [0x68, 0x0, 0x18, 0x38, 0x07]

cdChangeReq2 =     [0x68, 0x00, 0x18, 0x38, 0x06]
cdPollReq =        [0x68, 0x00, 0x18, 0x01]
scanTrackReq2 = [0x68, 0x00, 0x18, 0x38, 0x04]

msgList = [[statReq2,6,0,0],
           [stopPlayingReq2,6,0,0],
           [pausePlayingReq2,6,0,0],
           [trackChangeNextReq2,6,0,0],
           [trackChangePrevReq2,6,0,0],
           [cdChangeReq2,5,0,0],
           [randomModeReq2,5,0,0],
           [introModeReq2,5,0,0],
           [scanTrackReq2,5,0,0],
           [yatourPoll2,5,0,0],
           [cdPollReq,  4,0,0]]


class Ibus(serialConnection.SerialPort):
    cdNumber = 1
    trackNumber = 1
    isAnnouncementNeeded = False
    cdStatus = CD_STATUS_PLAYING
    random = False
    intro = 0
    
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
        tempTracknbr = (self.trackNumber % 10) | int(self.trackNumber / 10) << 4    
        message = message + self.cdStatus + [0x00, 0x3F, 0x00] + [self.cdNumber, tempTracknbr] 
        checksum = self.checkSumInject(message, len(message))
        #add checksum at the end
        message = message + [checksum]
        print("Send status: " + self.hexPrint(message, len(message)))
        self.sendIbus(message)
        
        
    #Timer to announce CD every 25-30 s
    def announceCallback(self):
        #if self.isAnnouncementNeeded:
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
            
    def clearInput(self):
        if hasattr(self, 'serialDev'):  
            self.serialDev.flushInput()
        else:
            print("Serial in NOT opened " + self.serialName)       
    def handleIbusMessage(self,message):
        global ibusPos
        global ibusbuff
        prefix = "Last handled msg: "
      
        if message == cdpoll[0:4]:
            prefix = prefix + "Radio poll req"
            #self.isAnnouncementNeeded = False
            self.sendIbus(radioPollResp)
            
        if message == yatourPoll[0:5]:
            prefix = prefix + "YATOUR Poll req"
            #self.sendIbus(cdpoll)
            
        elif message == statReq[0:6]:
            prefix = prefix + "staus/info request"
            self.sendStatus()
            #self.sendIbus(startPlayResp)
        elif message == stopPlayingReq[0:6]:
            prefix = prefix + "stop play request"
            self.cdStatus = CD_STATUS_NOT_PLAYING
            self.sendStatus()
            
        elif message == pausePlayingReq[0:6]:  
            prefix = prefix + "pause play request"
            self.cdStatus = CD_STATUS_PAUSE
            self.sendStatus()
            
        elif message == startPlayReq[0:6]:
            prefix =prefix + "start play request"
            self.cdStatus = CD_STATUS_PLAYING
            self.sendStatus()
            
            #here some of message prameters may vary so only static part is compared
        elif message[0:5] == cdChangeReq[0:5]:
            #extracting parameters
            if ibusbuff[ibusPos-1] > 0:
                self.cdNumber = ibusbuff[0]
            else:
                self.cdNumber = 1;    
            prefix = prefix + "CD change request. Cd to load: " + str(self.cdNumber)
                
            self.cdStatus = CD_STATUS_END_PLAYING;
            self.sendStatus()    
            self.cdStatus = CD_STATUS_PLAYING;
            self.sendStatus() 
            
        elif message == trackChangePrevReq[0:6]:
            self.trackNumber = (self.trackNumber - 1) % 60
            prefix = prefix + "Track previous request. Track: " + str(self.trackNumber)
            self.cdStatus = CD_STATUS_END_PLAYING;
            self.sendStatus()    
            self.cdStatus = CD_STATUS_PLAYING;
            self.sendStatus() 
            self.kodi.Player.GoTo({"playerid":0, "to":self.trackNumber}) 
           
        elif message == trackChangeNextReq[0:6]:
            self.trackNumber = (self.trackNumber + 1) % 60
            prefix = prefix + "Track next request. Track: " + str(self.trackNumber)
            #self.cdStatus = CD_STATUS_END_PLAYING;
            #self.sendStatus()   
            self.kodi.Player.GoTo({"playerid":0, "to":self.trackNumber})   
            self.cdStatus = CD_STATUS_PLAYING;
            self.sendStatus()
       
         
        elif message[0:5] == randomModeReq[0:5]:
            
            if ibusbuff[ibusPos-1] == 0x01:
                
                self.random = True
            else:
                self.random = False
        
            prefix = prefix + "Random mode: " + str(self.random)    
            self.sendStatus()    
        
        elif message[0:5] == introModeReq[0:5]:
            
            if ibusbuff[ibusPos-1] == 0x01:
                
                self.intro = True
            else:
                self.intro = False
        
            prefix = prefix + "Intro mode: " + str(self.intro)    
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
            self.sendStatus()    

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
            if ibusbuff[0:3] == header1 or ibusbuff[0:3] == header2 or ibusbuff[0:3] == header3 or ibusbuff[0:3] == header4 or ibusbuff[0:3] == header5:
                print("Got message to CD changer")
                lenght = ibusbuff[1]+2
                #if self.checkSumCalculator(ibusbuff[0:lenght], lenght): #do we really need this now?
                self.handleIbusMessage(ibusbuff[0:lenght])
                    #removing message as it was handled
                ibusbuff[0:lenght] = []
                ibusPos = len(ibusbuff)

            else:
                #shift left
                #print("Cutting " + str(bytesRead))
                ibusbuff[0:bytesRead] = []
                ibusPos = ibusPos - bytesRead 
    
    def receiveTest(self):
        global ibusPos
        global ibusbuff
        n = 1
        if n != 0:
            for i in range(0,len(trackChangeNextReq)):
                if ibusPos >= 64:
                    ibusPos = 0
                
                self.receiveIbusMessages2(trackChangeNextReq[i])
                      
         
    def receive(self):
        global ibusPos
        global ibusbuff

        n = self.serialDev.inWaiting()
        if n != 0:

            out = self.serialDev.read(n)

            for i in range(n):    
                self.receiveIbusMessages2(out[i])
            #print("Received " +str(ibusPos) + "  " + self.hexPrint(ibusbuff, len(ibusbuff)))   
        else:
            time.sleep(0.01)   
        
    def receiveIbusMessages2(self, c):
        global ibusPos
        global ibusbuff
        #print(str(hex(c)))
        #msg[2] is current pos
        #msg[0] is message
        #msg[3] is crc
        for msg in msgList:
            if msg[2] == 1:
                msg[0][1] =  c   
                
            msg[3] = msg[3] ^ c
            
            if msg[2] > 3 and msg[2] == msg[0][1] + 1:
                if msg[3] == 0:
                    self.handleIbusMessage(msg[0])
                else:
                    print("Wrong crc")
                    
                #reset 
                for msgtmp in msgList:
                    msgtmp[2] = 0
                    msgtmp[3] = 0
                    ibusPos = 0;
                break
            if msg[2] < msg[1] and msg[0][msg[2]] != c:
                msg[2] = 0
                msg[3] = 0
                continue
            
            if msg[2] >= msg[1]:
                ibusbuff[ibusPos] = c
                ibusPos = ibusPos +1
                
            msg[2] = msg[2] +1 
        
            #print(str(msg))        
                
                
import unittest

class IbusUt(unittest.TestCase):
    def test_uno(self):
        print("Im a test")
    
    
    
if __name__ == "__main__":
    unittest.main(verbosity=2)