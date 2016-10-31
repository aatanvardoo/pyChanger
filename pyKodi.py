from kodijson import Kodi
import threading
import time
current_milli_time = lambda: int(round(time.time() * 1000))
class ibusKodi(Kodi):
    kodi = Kodi("http://192.168.10.1:8080/jsonrpc", "kodi", "kodi")
    cdNumber = 1
    trackNumber = 1
    preDefPlaylist=["/media/pi/Adus/DiscoPolo", "/media/pi/Adus/Dance","/media/pi/Adus/Nowe"]
    percentage = 0
    numberOfPlaylist = 0 #[0:xx]
    playlists=[]
    def __init__(self):
        print( self.kodi.JSONRPC.Ping())
        self.initPlaylists()
        self.setPlaylist()
        self.playSong()
        
    def playSong(self):
        self.kodi.Player.GoTo({"playerid":0, "to":self.trackNumber-1})
                 
    def stopPlay(self):
        self.kodi.Player.PlayPause({"playerid":0})
               
    def initPlaylists(self):
        out = self.kodi.Files.GetDirectory({"directory":"special://profile/playlists/music"}) 
        self.numberOfPlaylist = out['result']['limits']['total']  
           
        self.playlists = out['result']['files']
        for i in range(self.numberOfPlaylist):
            print(self.kodi.AudioLibrary.Scan({"directory":self.playlists[i]['file']}))     
        print(str(out))
        
        
    def setPlaylist(self):
        if self.cdNumber <= self.numberOfPlaylist and self.cdNumber > 0:
            now  = current_milli_time()
            result = self.kodi.Playlist.Clear({"playlistid":0 }) #playlist 0 is audio playlist
            print("Clear result: " + str(result))
            result = self.kodi.AudioLibrary.Scan({"directory":self.playlists[self.cdNumber-1]['file']})
            print("SCAN result: " + str(result))
            result = self.kodi.Playlist.Add({"item":{"directory":self.preDefPlaylist[self.cdNumber-1]},"playlistid":0})
            print("Add result: " + str(result))
            out = self.kodi.Playlist.GetItems({"playlistid":0, "limits":{"end":1},"sort":{"order":"ascending","method":"dateadded"}})
            print("PLaylist track limits: " + str(out['result']['limits']))
            self.kodiTrNumbers = out['result']['limits']['total'] #total tracks in current Playlist
            result = self.kodi.Player.Open({"item":{"playlistid":0},"options":{"repeat":"all"}})
            print("Open result: " + str(result)+ " number of tracks " + str(self.kodiTrNumbers))
            then = current_milli_time()
            then = then - now
            print(str(then))
        else:
            print("ERROR cd number out of range! CD: " + str(self.cdNumber) + " playlists: " + str(self.numberOfPlaylist))

 
        
        
        
