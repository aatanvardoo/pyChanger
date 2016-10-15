from pyIbus import Ibus
phoneLed1=[0xC8,0x04,0xF0,0x2B,0x54,0x43]
pasuePlayingResp = "\x18\x0a\x68\x39\x01\x0c\x00\x01\x00\x01\x04\x4a"
llok = [0xC8,0x04,0xF0]

def main():
    print("Dziala!")
    
    print(pasuePlayingResp.find("\x39\x01\x0c"))
    phoneLed1.index(llok)
    #ibusk = Ibus()
    #ibusk.handleIbusMessage([0x1])
    #ibusk.receiveTest()

                

if __name__ == "__main__":
    main()