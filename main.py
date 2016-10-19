from serialConnection import SerialPort
from pyIbus import Ibus
import time
import threading
import pyIbus


from kodijson import Kodi


isPoolNeeded = True
phoneLed1=[0xC8,0x04,0xF0,0x2B,0x54,0x43]
phoneLedRed= [0xC8,0x04,0xF0,0x2B,0x01]
phoneLedGreen = [0xC8,0x04,0xF0,0x2B,0x10]
phoneLedYellow= [0xC8,0x04,0xF0,0x2B,0x04]



def main():

    print("Dziala!")
    time.sleep(40) #we are giving time to setup everything before python is up
    #kodi = Kodi("http://192.168.10.1:8080/jsonrpc", "kodi", "kodi")
    #print( kodi.JSONRPC.Ping())
    
    #print(str(kodi.Playlist.GetPlaylists()))
    #print(str(kodi.Playlist.GetItems(playlistid=0)))
    
    #print(str(kodi.Player.Open({"item":{"playlistid":0},"options":{"repeat":"all"}})))

    ibusDev = Ibus() 
    print(str(ibusDev.kodi.Playlist.GetPlaylists()))
    print(str(ibusDev.kodi.Playlist.Clear({"playlistid":0 })))
    print(str(ibusDev.kodi.Playlist.Add({"item":{"directory":"special://profile/playlists/music/Dance.xsp"},"playlistid":0})))
    print(str(ibusDev.kodi.Playlist.GetItems({ "properties": ["title", "album", "artist", "duration"], "playlistid": 0 })))
 
    ibusDev.sendIbusAndAddChecksum(phoneLedYellow)
    time.sleep(0.5)
    ibusDev.sendIbusAndAddChecksum(phoneLedRed)
    time.sleep(0.5)
    ibusDev.sendIbusAndAddChecksum(phoneLedGreen)
    ibusDev.clearInput()
    ibusDev.sendStatus()#playing status
    
    ibusDev.kodi.Player.Open({"item":{"playlistid":0},"options":{"repeat":"all"}})
    print(str(ibusDev.kodi.Player.GetActivePlayers()))
    print(str(ibusDev.kodi.Player.GoTo({"playerid":0, "to":1})))
     
    while True:
        ibusDev.receive()
                

if __name__ == "__main__":
    main()