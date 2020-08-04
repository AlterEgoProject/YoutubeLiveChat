import argparse
import serial
from time import sleep

ZEN = "".join(chr(0xff01 + i) for i in range(94))
HAN = "".join(chr(0x21 + i) for i in range(94))

ZEN2HAN = str.maketrans(ZEN, HAN)

keys_list = {
    'a': 'Button A',
    'b': 'Button B',
    'x': 'Button X',
    'y': 'Button Y',
    'q': 'HAT LEFT',
    'w': 'HAT TOP',
    'e': 'HAT RIGHT',
    's': 'HAT BOTTOM',
    '4': 'LX MIN',
    '8': 'LY MIN',
    '6': 'LX MAX',
    '2': 'LY MAX',
    'l': 'Button L',
    'k': 'Button ZL',
    'r': 'Button R',
    't': 'Button ZR',
    'u': 'RY MAX',
    'd': 'RY MIN',
    'p': 'Button START',
    '1': [], '3': [], '7':[], '9':[]
}

class PutSerial:
    def __init__(self, port):
        self.ser = serial.Serial(port, 9600)

    def send(self, msg, duration=0.2):
        msg = msg.translate(ZEN2HAN).lower()
        print(msg)
        self.ser.write(f'{msg}\r\n'.encode('utf-8'))
        sleep(duration)
        self.ser.write(b'RELEASE\r\n')

    def press_key(self, keys):
        # if len(keys) > 10:
        #     return
        for key in keys:
            if key in keys_list.keys():
                if key in ['1','2','3','4','6','7','8','9',]:
                    if key in ['1', '3', '7', '9']:
                        if key == '1':
                            self.send(keys_list['4'])
                            self.send(keys_list['2'])
                        elif key == '3':
                            self.send(keys_list['2'])
                            self.send(keys_list['6'])
                        elif key == '7':
                            self.send(keys_list['4'])
                            self.send(keys_list['8'])
                        else:  # key == '9':
                            self.send(keys_list['8'])
                            self.send(keys_list['6'])
                    else:
                        self.send(keys_list[key])
                    # sleep(0.2)
                    # send('RX CENTER')
                    # send('RY CENTER')
                else:
                    self.send(keys_list[key])
                    # sleep(0.2)

# try:
#     while True:
#         sleep(0.1)
#         send('Button A', 0.1)
# except KeyboardInterrupt:
#     send('RELEASE')
#     ser.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('port')
    args = parser.parse_args()
    ps = PutSerial(args.port)
    while(1):
        keys = input()
        ps.press_key(keys)
