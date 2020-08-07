from getURL import get_live_url
from getChat import GetChat
import typeKey
from putSerial import PutSerial
import beep

import argparse
import time
import random


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('port')
    args = parser.parse_args()

    target_url = 'https://www.youtube.com/live_chat?v=' + get_live_url()
    timestamp = None
    gc = GetChat(target_url, timestamp)
    ps = PutSerial(args.port)
    zero_chat_counter = 0
    flag = 'randomwalk'
    while(1):
        if gc.old_timestamp == None:
            gc.get()
            continue
        chats = gc.get()
        # print(len(chats))
        for chat in chats:
            if zero_chat_counter > 60 * 2:
                beep.beep(2000)
                beep.beep(2000)
                beep.beep(2000)
                beep.beep(2000)
            zero_chat_counter = 0
            text = chat[1]
            print(chat[0], text)
            if text == 'randomwalk':
                print('Mode randomwalk')
                flag = 'randomwalk'
            elif text == 'shootingstar':
                print('Mode shootingstar')
                flag = 'shootingstar'
            else:
                # typeKey.press_key(text)
                ps.press_key(text)
        if len(chats)==0:
            zero_chat_counter += 1
            if zero_chat_counter > 60 * 2:
                # ランダムウォーク
                if flag == 'randomwalk':
                    time.sleep(0.3)
                    ps.press_key('b' + random.choice(['2', '4', '6', '8']) * 3 + 'y')
                    time.sleep(0.5)
                    ps.press_key('b' + random.choice(['2', '4', '6', '8']) * 3 + 'y')
                # 祈り
                elif flag == 'shootingstar':
                    ps.press_key('sua')
            else:
                time.sleep(1)


if __name__ == '__main__':
    main()
    # print(sys.argv)
    # print(len(sys.argv))
