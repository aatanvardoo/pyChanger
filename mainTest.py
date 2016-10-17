from pyIbus import Ibus
import time
phoneLed1=[0xC8,0x04,0xF0,0x2B,0x54,0x43]
pasuePlayingResp = "\x18\x0a\x68\x39\x01\x0c\x00\x01\x00\x01\x04\x4a"
llok = [0xC8,0x04,0xF0]
current_milli_time = lambda: int(round(time.time() * 1000))
def main():
    print("Dziala!")
    
    ibusk = Ibus()

    ibusk.receiveTest()



                

if __name__ == "__main__":
    main()