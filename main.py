from getChat import GetChat
import typeKey
from putSerial import PutSerial

import argparse
import time
import random

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('port')
    parser.add_argument('v')
    args = parser.parse_args()

    # v = 'J1pBGkQI8aY'
    # if len(sys.argv) == 1:
    # else:
    #     v = sys.argv[1]
    target_url = 'https://www.youtube.com/live_chat?v=' + args.v
    timestamp = None
    gc = GetChat(target_url, timestamp)
    ps = PutSerial(args.port)
    zero_chat_counter = 0
    while(1):
        if gc.old_timestamp == None:
            chats = gc.get()
            continue
        chats = gc.get()
        # print(len(chats))
        for chat in chats:
            zero_chat_counter = 0
            text = chat[1]
            # typeKey.press_key(text)
            print(chat[0], text)
            ps.press_key(text)
        if len(chats)==0:
            time.sleep(1)
            zero_chat_counter += 1
            if zero_chat_counter > 60 * 5:
                ps.press_key('b')
                rand_direction = random.choice(['2', '4', '6', '8'])
                ps.press_key(rand_direction * 5)
                ps.press_key('y')

if __name__ == '__main__':
    main()
    # print(sys.argv)
    # print(len(sys.argv))
