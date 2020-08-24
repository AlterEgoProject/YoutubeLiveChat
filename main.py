from py import systems
from py.others import beep, line

import argparse
import time
import threading

import matplotlib.pyplot as plt
import numpy as np

import traceback


ps = None


def main():
    # print('start')
    parser = argparse.ArgumentParser()
    parser.add_argument('port')
    args = parser.parse_args()
    # print('read arg')
    target_url = 'https://www.youtube.com/live_chat?v=' + systems.get_live_url()
    timestamp = None
    gc = systems.GetChat(target_url, timestamp)
    ps = systems.PutSerial(args.port)
    ow = systems.ObsWebsket()
    # print('make obj')
    pw = systems.PlotWindow()
    volume_tread = threading.Thread(target=pw.start)
    volume_tread.start()
    # print('set vol')
    automove = systems.AutoMove(ps, ow)
    # print('set automove')

    while(1):
        # try:
        # print(gc.old_timestamp)
        if gc.old_timestamp is None:
            gc.get()
            continue
        chats = gc.get()
        # print(len(chats))
        # print(automove.zero_chat_counter)
        if automove.is_afk():
            if len(chats) == 0:
                if automove.is_field():
                    automove.afk_act()
            else:
                automove.deactivate_afk()

        for chat in chats:
            automove.zero_chat_counter = 0
            ow.set_icon_invisible('learning_counter')
            text = chat[1]
            print(text)
            # print(chat[2], text)
            if text[0] == '#':
                continue
            if len(automove.futures) > 0:
                automove.end_thread(text)
            else:
                if len(automove.thread_list) > 0:
                    automove.end_thread(text)
                if not(automove.is_command(text)):
                    ps.press_key(text)

        time.sleep(1)
        # except Exception as e:
        #     print(e)


if __name__ == '__main__':
    import sys
    flag = True
    while(1):
        try:
            main()
        except KeyboardInterrupt:
            break
        except Exception as e:
            beep.beep(2000, 200)
            except_str = traceback.format_exc()
            tb = sys.exc_info()[2]
            try:
                if ps.sender.isOpened():
                    ps.sender.closeSerial()
            except:
                pass
            print('{0}\nエラー、5秒後再起動します'.format(e.with_traceback(tb)))
            time.sleep(5)
            if flag:
                msg = "message:{0}".format(except_str)
                print(line.line(msg))
                flag = False
                continue

    # print(sys.argv)
    # print(len(sys.argv))
