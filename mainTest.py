from queue import Queue
import time
import threading
phoneLed1=[0xC8,0x04,0xF0,0x2B,0x54,0x43]
pasuePlayingResp = "\x18\x0a\x68\x39\x01\x0c\x00\x01\x00\x01\x04\x4a"
llok = [0xC8,0x04,0xF0]
current_milli_time = lambda: int(round(time.time() * 1000))

qu = Queue()


#Timer to announce CD every 25-30 s
class dupa():
    def announceCallback(self):
        print("jestem")
        if not qu.empty():
            item  = qu.get()
            func = item[0]
            func()
        threading.Timer(1, self.announceCallback).start()
        
    def test(self):
        print("cos")
    def put(self):
        
        qu.put((self.test,0))
        
def main():
    print("Dziala!")
    a = dupa()
    a.put()
    a.announceCallback()
    while True:
        a=1
    


                

if __name__ == "__main__":
    main()