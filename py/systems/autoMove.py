import time
from py.others import beep
import random
import threading
from concurrent.futures import ThreadPoolExecutor
from py import systems

AFK_SEC = 2 * 60
LEARNING_SEC = 60

afk_command = [
    'randomwalk',
    'shootingstar',
    'sandplay',
    'rolypoly',
    'stop'
]
auto_command = [
    'fishing',
    'rock',
    'learning',
    'step0',
    'step0.5',
    'step1',
    'step2',
    'step3',
    'step4',
    'step5',
    'go',
    'back',
]

class AutoMove:
    def __init__(self, ps, ow):
        self.zero_chat_counter = 0
        self.select = 'sandplay'  # 'shootingstar'  # 'randomwalk' 'sandplay'
        self.ps = ps
        self.ow = ow
        self.thread_list = []
        self.futures = []
        self.executor = ThreadPoolExecutor()
        self.roop_counter = 0
        self.learning_counter = 0
        self.old_select = 'sandplay'
        self.end_future()

    def set(self, text):
        self.select = text
        self.old_select = text
        print('Mode {}'.format(text))

    def is_command(self, text):
        if text in afk_command:
            self.set(text)
            return True
        elif text in auto_command or text[:8] == 'timeskip':
            self.auto_act(text)
            return True
        else:
            return False

    def auto_act(self, text):
        if text == 'fishing':
            self.ps.press_key('a')
            plotwin = systems.PlotWindow(self.ps)
            t = threading.Thread(target=plotwin.fishing)
            t.start()
            self.thread_list.append(t)
        elif text == 'rock':
            for _ in range(25):
                self.ps.press_key('a.')
        elif text == 'learning':
            if self.ow.is_field():
                self.ps.press_key('ds')
                time.sleep(1)
                self.learning_act()
            else:
                print('室内じゃ使えないよ！')
        elif text[:8] == 'timeskip':
            if self.ow.is_field():
                flag, msg, diff_list = self.check_timeskip(text)
                if flag is False:
                    print(msg)
                    return
                print(diff_list)
                self.ps.save_game()
                # 時間操作
                self.ps.change_time(diff_list)
                # タイトル画面
                for _ in range(90):
                    if self.ow.is_title():
                        break
                    time.sleep(1)
                time.sleep(2)
                self.ps.press_key('a')
            else:
                print('室内じゃ使えないよ！')
        elif text == 'step0':
            self.ps.press_key('ab-a-ab-ab-ab-ab-a.2ab-ab-')
        elif text == 'step0.5':
            self.ps.press_key('8-9-ab---')
            self.ps.press_key('ab-a-ab-ab-ab-ab-a.2ab-ab-')
        elif text == 'step1':
            self.ps.press_key('6-8ab-a-ab-ab-ab-ab-a.2ab-ab-')
        elif text == 'step2':
            self.ps.press_key('ab-ab-------ab--a')
            time.sleep(1)
            self.ps.press_key('a.a.a.a.a.a.a.a.a')
        elif text == 'step3':
            self.ps.press_key('b.b-b.b-b.b.b.b8-----ua')
        elif text == 'step4':
            self.ps.press_key('2-----99ab-')
            self.ps.press_key('ab-ab-ab-ab-ab-ab')
        elif text == 'step5':
            self.ps.press_key('ab-ab-ab-ab-ab-ab')
        elif text == 'go':
            self.ps.press_key('6-8ab-a-ab-ab-ab-ab-a.2ab-ab-')
            self.ps.press_key('ab-ab-------ab--a')
            time.sleep(1)
            self.ps.press_key('ab.ab.ab.ab.ab.')
            self.ps.press_key('ab.ab.ab.ab.ab.')
            time.sleep(12)
            self.ps.press_key('b.b-b.b-b.b.b.b8-----ua')
        elif text == 'back':
            self.ps.press_key('2-----99ab-')
            self.ps.press_key('ab-ab-ab-ab-ab-ab')

    @staticmethod
    def check_timeskip(text):
        flag = False
        msg = ''
        l = text.split(' ')
        diff_list = []
        if len(l) != 6:
            msg = '入力形式は「timeskip 年 月 日 時 分」です'
        else:
            for i in range(1,6):
                try:
                    num = int(l[i])
                    if abs(num) > 30:
                        msg = '数値の範囲は -30～30 です'
                        break
                    diff_list.append(num)
                except:
                    msg = '年月日時分には整数を入れてください'
                    break
            else:
                flag = True
        return flag, msg, diff_list


    def is_afk(self):
        self.zero_chat_counter += 1
        return self.zero_chat_counter > AFK_SEC

    def is_field(self):
        if self.ow.is_field():
            return True
        else:
            print('\r自動行動停止         ', end='')
            self.ps.press_key('sdbba')
            self.ps.press_key('2')
            self.roop_counter += 1
            if self.roop_counter > 60:
                self.ps.press_key(random.choice(['1', '3', '7', '9']) + 'x')
                self.roop_counter = 0
            self.end_future('')
            return False

    def learning_act(self):
        self.learning_counter = 0
        self.old_select = self.select
        self.select = 'stop'
        future = self.executor.submit(self.ow.test)
        self.futures.append(future)

    def afk_act(self):
        if self.select in auto_command:
            return
        if self.select == 'randomwalk' or self.select == 'sandplay':
            # self.learning_counter += 1
            # self.ow.set_icon_visible('learning_counter')
            # self.ow.set_text('learning_counter', str(LEARNING_SEC-self.learning_counter))
            # if self.learning_counter > LEARNING_SEC - 1:
            #     self.learning_act()

            # ランダムウォーク
            if self.select == 'randomwalk':
                print('\rランダムウォーク (歩いて拾う)', end='')
                # self.ps.press_key('dsb' + random.choice(['2', '4', '6', '8']) * 2 + 'y')
                self.ps.press_key('dsb' + random.choice(['2', '4', '6', '8']) * 2)
            # 明度の高い方へ歩きやすい
            elif self.select == 'sandplay':
                print('\r砂遊び (明るい方へ進みやすい)', end='')
                light_dist = self.ow.light_distribution()
                # self.ow.set_icon_visible('lightness')
                # str_lightness = '{:00}%       {:00}%\n\n\n{:00}%       {:00}%' \
                #     .format(int(light_dist[0] * 100),
                #             int(light_dist[1] * 100),
                #             int(light_dist[2] * 100),
                #             int(light_dist[3] * 100))
                # self.ow.set_text('lightness', str_lightness)
                for _ in range(2):
                    rand = random.random()
                    cum = 0
                    direction = ['7', '9', '1', '3']
                    for i in range(3):
                        cum += light_dist[i]
                        if rand < cum:
                            key = direction[i]
                            break
                    else:
                        key = direction[-1]
                    # self.ps.press_key('dsb' + key * 2 + 'y')
                    self.ps.press_key('dsb' + key * 2 )
        # 祈り
        elif self.select == 'shootingstar':
            print('\r流れ星モード          ', end='')
            self.ps.press_key('suba')

        # ダンゴムシ歩き
        elif self.select == 'rolypoly':
            print('\rダンゴムシモード (未実装)    ', end='')
            # 移動方向と距離から想定される距離を歩けなかった場合に
            # 向きを左右交互に変えて歩き続ける
            # before_img = self.ow.get_snap()
            # from_dir = rolypoly.get('from_direction', '2')
            # roll_right = rolypoly.get('roll_right', True)
            # to_dir, to_n = change_direction(from_dir, roll_right)
            # self.ps.press_key(to_dir*to_n)
            #
            # after_img = self.ow.get_snap()
            # distance = measure_distance(before_img, after_img)
            # rolypoly['from_direction'] = to_dir
            # if is_expected_move(distance, to_dir):
            #     rolypoly['roll_right'] = roll_right
            # else:
            #     rolypoly['roll_right'] = not roll_right
        elif self.select == 'stop':
            self.learning_counter += 1
            self.ow.set_text('learning_counter', str(LEARNING_SEC - self.learning_counter))
            if self.learning_counter > LEARNING_SEC - 1:
                self.end_future('')
                self.select = self.old_select
        # elif self.select == 'teach':
        #     if self.zero_chat_counter > 5 * 60:
        #         automove = AutoMove(self.ps, self.ow)
        #         t = threading.Thread(target=automove.ow.test)
        #         t.start()

    def deactivate_afk(self):
        beep.beep(2000)
        beep.beep(2000)
        beep.beep(2000)
        beep.beep(2000)
        self.zero_chat_counter = 0
        # self.ow.set_icon_invisible('lightness')

    def end_future(self, text=''):
        self.ow.text = text
        for future in self.futures:
            ans = future.result()
            if ans is True:
                self.ps.press_key('t..8.a')
            elif ans is False:
                self.ps.press_key('t..3.a')
        self.ow.text = None
        self.ow.set_icon_invisible('red_target')
        self.ow.set_icon_invisible('learning_counter')
        talk_items = ['talk_frame', 'talk_text', 'talk_rubi1', 'talk_rubi2']
        for name in talk_items:
            self.ow.set_icon_invisible(name)
        self.learning_counter = 0
        self.futures = []

    def end_thread(self, text=''):
        for tread in self.thread_list:
            tread.do_run = True
            tread.join()
        self.end_future(text)
        self.thread_list = []


if __name__ == '__main__':
    ps = None  # systems.PutSerial(args.port)
    ow = systems.ObsWebsket()
    automove = AutoMove(ps, ow)
    t = threading.Thread(target=automove.ow.test)
    t.start()
    print()
