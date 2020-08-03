import argparse
import serial
from time import sleep

parser = argparse.ArgumentParser()
parser.add_argument('port')
args = parser.parse_args()

def send(msg, duration=0.1):
    print(msg)
    ser.write(f'{msg}\r\n'.encode('utf-8'));
    sleep(duration)
    ser.write(b'RELEASE\r\n');

ser = serial.Serial(args.port, 9600)

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

def press_key(keys):
    # if len(keys) > 10:
    #     return
    for key in keys:
        if key in keys_list.keys():
            if key in ['1','2','3','4','6','7','8','9',]:
                if key in ['1', '3', '7', '9']:
                    if key == '1':
                        send(keys_list['4'])
                        send(keys_list['2'])
                    elif key == '3':
                        send(keys_list['2'])
                        send(keys_list['6'])
                    elif key == '7':
                        send(keys_list['4'])
                        send(keys_list['8'])
                    else:  # key == '9':
                        send(keys_list['8'])
                        send(keys_list['6'])
                else:
                    send(keys_list[key])
                # sleep(0.2)
                # send('RX CENTER')
                # send('RY CENTER')
            else:
                send(keys_list[key])
                # sleep(0.2)

# try:
#     while True:
#         sleep(0.1)
#         send('Button A', 0.1)
# except KeyboardInterrupt:
#     send('RELEASE')
#     ser.close()

if __name__ == '__main__':
    while(1):
        keys = input()
        press_key(keys)
