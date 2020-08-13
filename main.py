from getURL import get_live_url
from getChat import GetChat
import typeKey
from putSerial import PutSerial
from sound import PlotWindow
import beep

import argparse
import time
import random
import threading


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('port')
    args = parser.parse_args()

    target_url = 'https://www.youtube.com/live_chat?v=' + get_live_url()
    timestamp = None
    gc = GetChat(target_url, timestamp)
    ps = PutSerial(args.port)

    pw = PlotWindow()
    volume_tread = threading.Thread(target=pw.start)
    volume_tread.start()

    zero_chat_counter = 0
    afk = 'shootingstar'  # 'randomwalk'
    tread_list  = []
    while(1):
        # try:
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
            print(text)
            # print(chat[2], text)
            if text[0] == '#':
                continue
            if text == 'randomwalk':
                print('Mode randomwalk')
                afk = 'randomwalk'
            elif text == 'shootingstar':
                print('Mode shootingstar')
                afk = 'shootingstar'
            elif text == 'fishing':
                print('Mode fishing')
                ps.press_key('a')
                plotwin = PlotWindow(ps)
                t = threading.Thread(target=plotwin.fishing)
                t.start()
                tread_list.append(t)
            elif text == 'rock':
                for _ in range(30):
                    ps.press_key('a.')
            else:
                for tread in tread_list:
                    tread.do_run = True
                    tread.join()
                tread_list = []
                ps.press_key(text)
        if len(chats)==0:
            zero_chat_counter += 1
            if zero_chat_counter > 60 * 2:
                # if is_map_appear():
                # ランダムウォーク
                if afk == 'randomwalk':
                    print('\rランダムウォーク (歩いて拾う)', end='')
                    ps.press_key('b' + random.choice(['2', '4', '6', '8']) * 2 + 'y' +
                                 random.choice(['2', '4', '6', '8']) * 2 + 'y' +
                                 random.choice(['2', '4', '6', '8']) * 2 + 'y' +
                                 random.choice(['2', '4', '6', '8']) * 2 + 'y')
                # 祈り
                elif afk == 'shootingstar':
                    print('\r流れ星モード (uba)', end='')
                    ps.press_key('uba')
            else:
                time.sleep(1)
        # except Exception as e:
        #     print(e)


if __name__ == '__main__':
    import line
    import sys
    flag = True
    while(1):
        try:
            main()
        except KeyboardInterrupt:
            break
        except Exception as e:
            tb = sys.exc_info()[2]
            print('{0}\nエラー、5秒後再起動します'.format(e.with_traceback(tb)))
            time.sleep(5)
            if flag:
                msg = "message:{0}".format(e.with_traceback(tb))
                print(line.line(msg))
                flag = False
                continue

    # print(sys.argv)
    # print(len(sys.argv))
