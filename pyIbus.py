
from serialConnection import SerialPort
import time
import threading
from threading import Thread
from kodijson import Kodi
import RPi.GPIO as GPIO
from queue import Queue
import pyMessages
from pyKodi import ibusKodi
current_sec_time = lambda: int(round(time.time()))
current_milli_time = lambda: int(round(time.time() * 1000))


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


#queue for Ibus send
sendQ = Queue()
#queue for kodi send
sendKodiQ = Queue()
#queue for incoming msg
rcvKodiQ = Queue()

class myThread (Thread):
    def __init__(self, threadID, message):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.message = message
        self.st = False
    def run(self):
        print("Starting " + str(self.threadID))
        self.rcvTimeout(self.message)
        print("Exiting " + str(self.threadID))
        
    def stop(self):
        self.st = True
        
    def rcvTimeout(self, message):
        count = 0
        while count < 10 and self.st == False:
            time.sleep(0.1)
            count += 1
        if self.st == False:
            print("I'm sending message again")
            while not rcvKodiQ.empty(): 
                rcvKodiQ.get() #cleaning queue    
                sendQ.put(message)


class Ibus():
    channel = 17
    channel2 = 27 #1-6
    isAnnouncementNeeded = True
    cdStatus = CD_STATUS_PLAYING
    random = False
    intro = 0
    kodiTrNumbers = 60 #dummy value
    debugFlag = False
    CDCD = False

    def __init__(self, model):
        self.model = model
        #initialize kodi sub module
        self.kodi = ibusKodi()
        #initialize serial sub module
        self.com = SerialPort()
        self.initGpio()
        self.readKodi()
        
    def sendStatus(self):
        #compose status response
        message = [0x18,0x0a,0x68,0x39]
        if self.CDCD == True:
            self.CDCD =False
            message[0] = 0x76
        #is random mode on/off
        if self.random:
            self.cdStatus[1] = self.cdStatus[1] | 0x20 
        
        #is intro mode on off
        if self.intro:
            self.cdStatus[1] = self.cdStatus[1] | 0x10     
        #compose message
        tempTracknbr = (self.kodi.trackNumber % 10) | int(self.kodi.trackNumber / 10) << 4    
        message = message + self.cdStatus + [0x00, 0x3F, 0x00] + [self.kodi.cdNumber, tempTracknbr] 
        checksum = self.checkSumInject(message, len(message))
        #add checksum at the end
        message = message + [checksum]
        #print("Send status: " + self.hexPrint(message, len(message)))
        sendQ.put(message)
      
        
    #Timer to announce CD every 25-30 s
    def announceCallback(self):
        if self.isAnnouncementNeeded == True:
            self.sendIbusAndAddChecksum(pyMessages.yatourPoll)
        threading.Timer(10, self.announceCallback).start()

          
    def IbusSendTask(self):
        
        if not sendQ.empty():
            #check if IBUS is clear
            channel = GPIO.wait_for_edge(self.channel, GPIO.FALLING or GPIO.RISING, timeout=5)
            
            if channel is None:
                #GPIO.output(self.channel2, 1)
                #time.sleep(0.003)
                #GPIO.output(self.channel2, 0)
                #channel = GPIO.wait_for_edge(self.channel, GPIO.FALLING or GPIO.RISING, timeout=3)
                #if channel is None:
                    #for 5mil was no transmission. Can send  
                msg  = sendQ.get()#removed from here it consumes around 30us
                self.sendIbus(msg) #running func with arg
                  
            #GPIO.output(self.channel2, 0)
        threading.Timer(0.020, self.IbusSendTask).start()
        #Timer to announce CD every 25-30 s
    def sendToKodi(self):
        
        if not sendKodiQ.empty():
            item  = sendKodiQ.get()
            func = item[0]
            func()

        threading.Timer(0.2, self.sendToKodi).start()  
        
    def readKodi(self):
        out = self.kodi.kodi.Player.GetProperties({"properties":["position","percentage"], "playerid":0 })
        currentPerc = out['result']['percentage']
        currentTr = out['result']['position']
        #if self.kodiTrPos != self.trackNumber -1:
        if(currentPerc < self.kodi.percentage) and self.kodi.trackNumber != currentTr +1:
            self.kodi.trackNumber = currentTr + 1
            self.sendStatus()
            
        self.kodi.percentage = currentPerc
 
        threading.Timer(2, self.readKodi).start()      
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
        self.com.serialDev.flushOutput()
        self.com.serialDev.flushInput()
        self.com.serialDev.write(bytes(message))
        self.com.serialDev.flush() #waits untill all data is out
        #self.serialDev.flushInput()
        if(message[0:4] == pyMessages.testStat):
            thread = myThread(1, message)
            rcvKodiQ.put((message,thread))
            thread.start()

    
    def sendIbusAndAddChecksum(self,message):
        if hasattr(self.com, 'serialDev'):  
            checksum = self.checkSumInject(message, len(message))
            #add checksum at the end
            message = message + [checksum]
            sendQ.put(message)
            #self.serialDev.write(bytes(message)) 
        else:
            print("Serial in NOT opened " + self.com.serialName)
            
    def clearInput(self):
        if hasattr(self.com, 'serialDev'):  
            self.com.serialDev.flushInput()
            self.com.serialDev.flushOutput()
        else:
            print("Serial in NOT opened " + self.com.serialName)       
    def handleIbusMessage(self,message):
        global ibusPos
        global ibusbuff
        #now = current_milli_time()
        prefix = "Last handled msg: "
        self.clearInput()
        #time.sleep(0.005)
        if message == pyMessages.statReq:
            #prefix = prefix + "staus/info request"
            self.sendStatus()
        elif message == pyMessages.cdPollReq:
            self.isAnnouncementNeeded = False
            self.sendIbusAndAddChecksum(pyMessages.radioPollResp)
            
        elif message == pyMessages.statReqCDCD:
            self.CDCD= True    #do we really need this?
            self.sendStatus()
            
        elif message == pyMessages.stopPlayingReq[0:6]:
            prefix = prefix + "stop play request"
            self.cdStatus = CD_STATUS_NOT_PLAYING
            self.sendStatus()
            self.kodi.stopPlay()
            
        elif message == pyMessages.pausePlayingReq[0:6]:  
            prefix = prefix + "pause play request"
            self.cdStatus = CD_STATUS_PAUSE
            self.sendStatus()
            self.kodi.stopPlay()
            
        elif message == pyMessages.startPlayReq:
            prefix =prefix + "start play request"
            self.cdStatus = CD_STATUS_PLAYING
            self.sendStatus()
            sendKodiQ.put((self.kodi.playSong,0))
            #here some of message prameters may vary so only static part is compared
        elif message[0:5] == pyMessages.cdChangeReq[0:5]:
            #extracting parameters
            if ibusbuff[ibusPos-1] > 0:
                tempCd = ibusbuff[0]
            else:
                return
            
            #if CD number is valid if no doesnt set anything
            if tempCd <= self.kodi.numberOfPlaylist:
                self.kodi.cdNumber = tempCd
                self.kodi.trackNumber = 1
            else:
                return
   
            self.cdStatus = CD_STATUS_PLAYING;
            self.sendStatus() 
            
            sendKodiQ.put((self.kodi.setPlaylist,0))
            

        elif message == pyMessages.trackChangePrevReq or message == pyMessages.oldtrackChangePrevReq:
            
            if self.kodi.trackNumber - 1 <  1:
                self.kodi.trackNumber = self.kodiTrNumbers
            else:
                self.kodi.trackNumber  = self.kodi.trackNumber - 1
   
            self.cdStatus = CD_STATUS_PLAYING;
            self.sendStatus() 
            sendKodiQ.put((self.kodi.playSong,0))
            
        elif message == pyMessages.trackChangeNextReq or message == pyMessages.oldtrackChangeNextReq:
            
            if self.kodi.trackNumber + 1 >  self.kodiTrNumbers:
                self.kodi.trackNumber = 1
            else:
                self.kodi.trackNumber  = self.kodi.trackNumber + 1

            self.cdStatus = CD_STATUS_PLAYING;
            self.sendStatus()
            sendKodiQ.put((self.kodi.playSong,0))
            #self.trakChanged = True
         
        elif message[0:5] == pyMessages.randomModeReq:
            
            if ibusbuff[ibusPos-1] == 0x01:
                
                self.random = True
            else:
                self.random = False
        
            prefix = prefix + "Random mode: " + str(self.random)    
            self.sendStatus()    
        
        elif message[0:5] == pyMessages.introModeReq:
            
            if ibusbuff[ibusPos-1] == 0x01:
                
                self.intro = True
            else:
                self.intro = False
        
            prefix = prefix + "Intro mode: " + str(self.intro)    
            self.sendStatus()        
           
        elif message[0:5] == pyMessages.scanTrackReq:
            
            if self.cdStatus == CD_STATUS_PLAYING:
                #no scan if music is not playing
                if message[5] == 0x00:
                    self.cdStatus = CD_STATUS_SCAN_FORWARD
                else:
                    self.cdStatus = CD_STATUS_SCAN_BACKWARD
                    
            prefix = prefix + "Scanning. It is not HANDLED"
            #is this really needed?     
            self.sendStatus()
        elif message[0:4] ==  pyMessages.testStat:    
            if not rcvKodiQ.empty():    
                qitem = rcvKodiQ.get()
                msgtemp = qitem[0][0:11]
                func = qitem[1]
                #composing all status msg without crs
                message = message + ibusbuff[0:7]
                
                if message == msgtemp:
                    print("OKOK")
                    #we got what we send. Time to stop watchdog thread
                    func.stop()
        
        #time = current_sec_time()    
        #self.printDbg(str(time)+ "   " + prefix + '  ' + self.hexPrint(message,len(message)) + " length: " + str(len(message)) + " last: " + str(current_milli_time()-now) )   
            
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
            if ibusbuff[0:3] == header1 or ibusbuff[0:3] == header2 or ibusbuff[0:3] == header3:
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
            for i in range(0,len(pyMessages.cdChangeReq)):
                if ibusPos >= 64:
                    ibusPos = 0
                
                self.receiveIbusMessages2(pyMessages.cdChangeReq[i])
                      
         
    def receive(self):
        global ibusPos
        global ibusbuff

        n = self.com.serialDev.inWaiting()
        if n != 0:

            out = self.com.serialDev.read(n)

            for i in range(n):    
                self.receiveIbusMessages2(out[i])
            #print("Received bytes: " + str(n))   
        else:
            time.sleep(0.05)   
        
    def receiveIbusMessages2(self, c):
        global ibusPos
        global ibusbuff
        #print(str(hex(c)))
        #msg[2] is current pos
        #msg[0] is message
        #msg[3] is crc
        for msg in pyMessages.msgList:
            if msg[2] == 1:
                msg[0][1] =  c   
                
            msg[3] = msg[3] ^ c
            
            if msg[2] > 3 and msg[2] == msg[0][1] + 1:
                if msg[3] == 0:
                    #now = current_milli_time()
                    self.handleIbusMessage(msg[0])
                    #now = current_milli_time() - now
                    #print("last: " + str(now))
                else:
                    print("Wrong crc")
                    
                #reset 
                for msgtmp in pyMessages.msgList:
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
                 

    def initGpio(self):
        print("Initializing GPIO")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.channel, GPIO.IN)
        GPIO.setup(self.channel2, GPIO.OUT)
        GPIO.output(self.channel2, 0)                
import unittest

class IbusUt(unittest.TestCase):
    def test_uno(self):
        print("Im a test")
    
    
    
if __name__ == "__main__":
    unittest.main(verbosity=2)