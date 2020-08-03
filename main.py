from getChat import GetChat
import typeKey
from putSerial import PutSerial

import argparse
import time

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
    while(1):
        if gc.old_timestamp == None:
            chats = gc.get()
            continue
        chats = gc.get()
        # print(len(chats))
        for chat in chats:
            text = chat[1]
            # typeKey.press_key(text)
            ps.press_key(text)
            print(chat[0], text)
        if len(chats)==0:
            time.sleep(1)

if __name__ == '__main__':
    main()
    # print(sys.argv)
    # print(len(sys.argv))
