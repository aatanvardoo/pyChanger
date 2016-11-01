from kodijson import Kodi
import time
current_milli_time = lambda: int(round(time.time() * 1000))
class ibusKodi(Kodi):
    kodi = Kodi("http://192.168.10.1:8080/jsonrpc", "kodi", "kodi")
    cdNumber = 1
    trackNumber = 1
    kodiTrNumbers = 60 #dummy value
    preDefPlaylist=["/media/pi/Adus/DiscoPolo", "/media/pi/Adus/Dance","/media/pi/Adus/Nowe"]
    percentage = 0
    numberOfPlaylist = 0 #[0:xx]
    def __init__(self, debug):
        
        self.debug = debug
        self.pingKodi(40)
        self.initPlaylists()
        self.setPlaylist()
        self.playSong()
        
    
    def pingKodi(self,timeout):
        sec = 0;
        while sec < timeout:
            try:
                self.kodi.JSONRPC.Ping()
            except:
                self.dbgPrint("Kodi in not pingable")
            else:
                self.dbgPrint("Received Pong after " + str(sec*2))
                return
            time.sleep(2)
            sec += 1

    def playSong(self):
        self.kodi.Player.GoTo({"playerid":0, "to":self.trackNumber-1})
                 
    def stopPlay(self):
        self.kodi.Player.PlayPause({"playerid":0})
               
    def initPlaylists(self):
        self.numberOfPlaylist = len(self.preDefPlaylist)
        print("Number of playlists: " + str(self.numberOfPlaylist))
        
    def setPlaylist(self):
        if self.cdNumber <= self.numberOfPlaylist and self.cdNumber > 0:
            now  = current_milli_time()
            result = self.kodi.Playlist.Clear({"playlistid":0 }) #playlist 0 is audio playlist
            self.dbgPrint("Clear result: " + str(result))
            
            result = self.kodi.Playlist.Add({"item":{"directory":self.preDefPlaylist[self.cdNumber-1]},"playlistid":0})
            self.dbgPrint("Add result: " + str(result))
            
            out = self.kodi.Playlist.GetItems({"playlistid":0, "limits":{"end":1},"sort":{"order":"ascending","method":"dateadded"}})
            self.dbgPrint("PLaylist track limits: " + str(out['result']['limits']))
            
            self.kodiTrNumbers = out['result']['limits']['total'] #total tracks in current Playlist
            
            result = self.kodi.Player.Open({"item":{"playlistid":0},"options":{"repeat":"all"}})
            self.dbgPrint("Open result: " + str(result)+ " number of tracks " + str(self.kodiTrNumbers))
            
            then = current_milli_time()
            then = then - now
            self.dbgPrint("Reading kodi playlist info took: " + str(then))
            
        else:
            print("ERROR cd number out of range! CD: " + str(self.cdNumber) + " playlists: " + str(self.numberOfPlaylist))

 
    def dbgPrint(self, string):
        if self.debug:
            print(string)
        
        
