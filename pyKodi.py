

class pyKodi():
    
    def playSong(self):
        self.kodi.Player.GoTo({"playerid":0, "to":self.trackNumber-1})
                 
    def stopPlay(self):
        self.kodi.Player.PlayPause({"playerid":0})       
    
    def printDbg(self, toPrint):
        if self.debugFlag == True:
            print(toPrint)