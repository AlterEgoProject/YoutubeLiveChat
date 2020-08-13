from py.systems.getURL import get_live_url
from py.systems.getChat import GetChat
from py.systems.putSerial import PutSerial
from py.systems.sound import PlotWindow
from py.systems.connectOBS import ObsWebsket
from py.others import beep, line

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
    ow = ObsWebsket()

    pw = PlotWindow()
    volume_tread = threading.Thread(target=pw.start)
    volume_tread.start()

    zero_chat_counter = 0
    afk = 'sandplay'  # 'shootingstar'  # 'randomwalk' 'sandplay'
    rolypoly = {}
    thread_list  = []
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
            elif text == 'rolypoly':
                print('Mode rolypoly')
                afk = 'rolypoly'
            elif text == 'fishing':
                print('Mode fishing')
                ps.press_key('a')
                plotwin = PlotWindow(ps)
                t = threading.Thread(target=plotwin.fishing)
                t.start()
                thread_list.append(t)
            elif text == 'sandplay':
                print('Mode sandplay')
                afk = 'sandplay'
            elif text == 'rock':
                for _ in range(30):
                    ps.press_key('a.')
            else:
                for tread in thread_list:
                    tread.do_run = True
                    tread.join()
                thread_list = []
                ps.press_key(text)
        if len(chats)==0:
            zero_chat_counter += 1
            if zero_chat_counter > 60 * 2:
                first_image = ow.get_snap()
                ow.detect_clam(first_image)
                time.sleep(1)
                is_field = ow.is_field()
                ow.set_icon_invisible('red_target')

                if is_field is False:
                    print('\r自動行動停止         ', end='')
                    ps.press_key('db')
                    ps.press_key('2')
                else:
                    # ランダムウォーク
                    if afk == 'randomwalk':
                        print('\rランダムウォーク (歩いて拾う)', end='')
                        ps.press_key('db' + random.choice(['2', '4', '6', '8']) * 2 + 'y' +
                                     random.choice(['2', '4', '6', '8']) * 2 + 'y' +
                                     random.choice(['2', '4', '6', '8']) * 2 + 'y' +
                                     random.choice(['2', '4', '6', '8']) * 2 + 'y')
                    # 祈り
                    elif afk == 'shootingstar':
                        print('\r流れ星モード (uba)    ', end='')
                        ps.press_key('uba')
                    # 明度の高い方へ歩きやすい
                    elif afk == 'sandplay':
                        print('\r砂遊び (明るい方へ進みやすい)', end='')
                        light_dist = ow.light_distribution(first_image)
                        for _ in range(2):
                            rand = random.random()
                            cum = light_dist[0]
                            if rand < cum:
                                key = '7'
                            else:
                                cum += light_dist[1]
                                if rand < cum:
                                    key = '9'
                                else:
                                    cum += light_dist[2]
                                    if rand < cum:
                                        key = '1'
                                    else:
                                        key = '3'
                            ps.press_key('db' + key * 2 + 'y')
                    # ダンゴムシ歩き
                    elif afk == 'rolypoly':
                        print('\rダンゴムシモード (未実装)    ', end='')
                        # 移動方向と距離から想定される距離を歩けなかった場合に
                        # 向きを左右交互に変えて歩き続ける
                        # before_img = ow.get_snap()
                        # from_dir = rolypoly.get('from_direction', '2')
                        # roll_right = rolypoly.get('roll_right', True)
                        # to_dir, to_n = change_direction(from_dir, roll_right)
                        # ps.press_key(to_dir*to_n)
                        #
                        # after_img = ow.get_snap()
                        # distance = measure_distance(before_img, after_img)
                        # rolypoly['from_direction'] = to_dir
                        # if is_expected_move(distance, to_dir):
                        #     rolypoly['roll_right'] = roll_right
                        # else:
                        #     rolypoly['roll_right'] = not roll_right
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
