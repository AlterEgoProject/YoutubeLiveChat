import argparse
from time import sleep

from py.Commands.Sender import Sender
from py.Commands.UnitCommand import UnitCommand
from py.Commands.PythonCommandBase import PythonCommand, ImageProcPythonCommand
from py.Commands.Keys import KeyPress, Button, Hat, Direction, Stick

ZEN = "".join(chr(0xff01 + i) for i in range(94))
HAN = "".join(chr(0x21 + i) for i in range(94))

ZEN2HAN = str.maketrans(ZEN, HAN)

keys_list = {
    'a': Button.A,
    'b': Button.B,
    'x': Button.X,
    'y': Button.Y,
    'q': Hat.LEFT,
    'w': Hat.TOP,
    'e': Hat.RIGHT,
    's': Hat.BTM,
    '1': Direction(Stick.LEFT, -135, showName='DOWN_LEFT'),
    '2': Direction(Stick.LEFT, -90, showName='DOWN'),
    '3': Direction(Stick.LEFT, -45, showName='DOWN_RIGHT'),
    '4': Direction(Stick.LEFT, -180, showName='LEFT'),
    '6': Direction(Stick.LEFT, 0, showName='RIGHT'),
    '7': Direction(Stick.LEFT, 135, showName='UP_LEFT'),
    '8': Direction(Stick.LEFT, 90, showName='UP'),
    '9': Direction(Stick.LEFT, 45, showName='UP_RIGHT'),
    'l': Button.L,
    'k': Button.ZL,
    'r': Button.R,
    't': Button.ZR,
    'u': Direction(Stick.RIGHT, 90, showName='UP'),
    'd': Direction(Stick.RIGHT, -90, showName='DOWN'),
    'p': Button.PLUS,
}


class Dammy:
    @staticmethod
    def get():
        return False


class PutSerial:
    def __init__(self, port):
        self.sender = Sender(Dammy)
        self.sender.openSerial(port)
        # self.unitcommand = UnitCommand()
        # self.unitcommand.start(self.sender)
        # self.keypress = KeyPress(self.sender)
        # self.ser = serial.Serial(port, 9600)
        self.command = PythonCommand()
        self.command.keys = KeyPress(self.sender)

    def test(self):
        self.command.press(Direction(Stick.LEFT, 120), 3, 1)
        self.command.keys.end()

    # def send(self, msg, duration=0.2):
    #     print(msg)
    #     self.sender.writeRow(msg)
    #     sleep(duration)
    #     # self.sender.writeRow(b'RELEASE\r\n')
    #     self.sender.writeRow(b'RELEASE\r\n')

    def press_key(self, keys):
        keys = keys.translate(ZEN2HAN).lower()
        # if len(keys) > 10:
        #     return
        for i in range(len(keys)):
            key = keys[i]
            hold_key = []
            if key in keys_list.keys():
                # -:1秒継続
                # .:0.2秒待機
                duration = 0.2
                wait_sec = 0
                for j in range(i, len(keys)):
                    if keys[j] == '-':
                        if wait_sec > 0:
                            break
                        duration += 1
                    elif keys[j] == '.':
                        wait_sec += 0.2
                    else:
                        break
                # (:直前のボタンをホールド
                # ):ホールドを解除
                if i < len(keys) - 1 and keys[i+1] == '(':
                    hold_key.append(key)
                    self.command.hold(keys_list[key])
                elif i < len(keys) - 1 and keys[i+1] == ')':
                    if len(hold_key) > 0:
                        self.command.holdEnd(hold_key.pop())
                else:
                    self.command.press(keys_list[key], duration, wait_sec)



# try:
#     while True:
#         sleep(0.1)
#         send('Button A', 0.1)
# except KeyboardInterrupt:
#     send('RELEASE')
#     ser.close()

if __name__ == '__main__':
    import time
    parser = argparse.ArgumentParser()
    parser.add_argument('port')
    args = parser.parse_args()
    ps = PutSerial(args.port)
    # ps.test()
    while(1):
        keys = input()
        ps.press_key(keys)
        # ps.send(keys)
