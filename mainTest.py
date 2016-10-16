from pyIbus import Ibus
import time
phoneLed1=[0xC8,0x04,0xF0,0x2B,0x54,0x43]
pasuePlayingResp = "\x18\x0a\x68\x39\x01\x0c\x00\x01\x00\x01\x04\x4a"
llok = [0xC8,0x04,0xF0]
current_milli_time = lambda: int(round(time.time() * 1000))
def main():
    print("Dziala!")
    
    ibusk = Ibus()
    #ibusk.handleIbusMessage([0x1])
    now = current_milli_time()
    ibusk.receiveTest()
    then = current_milli_time()
    print("time "+ str(then  - now))


                

if __name__ == "__main__":
    main()