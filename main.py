from getChat import GetChat
import typeKey
import putSerial

import sys
import time

def main():
    # if len(sys.argv) == 1:
    v = 'J1pBGkQI8aY'
    # else:
    #     v = sys.argv[1]
    target_url = 'https://www.youtube.com/live_chat?v=' + v
    timestamp = None
    gc = GetChat(target_url, timestamp)
    while(1):
        if gc.old_timestamp == None:
            chats = gc.get()
            continue
        chats = gc.get()
        # print(len(chats))
        for chat in chats:
            text = chat[1]
            # typeKey.press_key(text)
            putSerial.press_key(text)
            print(chat[0], text)
        if len(chats)==0:
            time.sleep(1)

if __name__ == '__main__':
    main()
    # print(sys.argv)
    # print(len(sys.argv))
