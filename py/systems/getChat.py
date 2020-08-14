from bs4 import BeautifulSoup
import requests

from datetime import datetime, timedelta
import random
from py.systems import connectOBS

exclude_list = [
]
CANTIDATE_MIN = 2
VALIDATE_SEC = 20
AFK_SEC = 60
LIMIT_MIN = 5


class GetChat:
    def __init__(self, target_url, old_timestamp=None):
        self.random_time = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23]
        # self.random_time = []
        self.target_url = target_url
        self.comment_data = []
        self.session = requests.Session()
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}

        self.old_timestamp = old_timestamp

        self.ticket = None
        self.ticket_flag = False
        self.name_list = []
        self.selected_time = datetime.now()
        self.afk_time = datetime.now()
        self.ow = connectOBS.ObsWebsket()

    def get(self):
        html = self.session.get(self.target_url, headers=self.headers)
        soup = BeautifulSoup(html.text, "html.parser")
        # print(soup)
        # exit(1)

        # 次に飛ぶurlのデータがある部分をfind_allで探してsplitで整形
        dict_str = ""
        for scrp in soup.find_all("script"):
            if "window[\"ytInitialData\"]" in scrp.text:
                dict_str = scrp.text.split(" = ")[1]

        # javascript表記なので更に整形. falseとtrueの表記を直す
        dict_str = dict_str.replace("false", "False")
        dict_str = dict_str.replace("true", "True")

        # 辞書形式と認識すると簡単にデータを取得できるが, 末尾に邪魔なのがあるので消しておく（「空白2つ + \n + ;」を消す）
        dict_str = dict_str.rstrip("  \n;")
        # 辞書形式に変換
        if len(dict_str) == 0:
            return []
        dics = eval(dict_str)

        # dics["contents"]["liveChatRenderer"]["actions"]がコメントデータのリスト。
        comment_data = []
        name_list = []
        timestamp = self.old_timestamp
        # try:
        for samp in dics["contents"]["liveChatRenderer"]["actions"]:
            try:
                temp = samp['addChatItemAction']['item']['liveChatTextMessageRenderer']
                timestamp = temp['timestampUsec']
                text = temp['message']['runs'][0]['text']
                # print(text)
                if '#' in text or '＃' in text:
                    continue
                name = temp['authorName']['simpleText']
                name_id = temp['id']
                delta_sec = datetime.now().timestamp() - int(timestamp)/1000/1000
                # print(temp['message']['runs'][0]['text'])
                if delta_sec < 60 * CANTIDATE_MIN:
                    name_list.append(name)
                # print(self.old_timestamp is None, int(self.old_timestamp) < int(timestamp))
                if self.old_timestamp is None or int(self.old_timestamp) < int(timestamp):
                    if name in exclude_list:
                        continue
                    # print(self.ticket is None, self.ticket == name)
                    if self.ticket is None or self.ticket == name:
                        if self.ticket == name:
                            # チケット有効化
                            self.afk_time = datetime.now()
                            if text[:4] == 'pass' or text[:2] == 'パス':
                                name_list_temp = set(self.name_list)
                                name_list_temp.discard(self.ticket)
                                self.name_list = list(name_list_temp)
                                if text[:4] == 'pass':
                                    pass_index = 4
                                else:
                                    pass_index = 2
                                if len(text) > pass_index and text[pass_index:] in self.name_list:
                                    self.ticket = text[pass_index:]
                                else:
                                    if len(self.name_list) == 0:
                                        self.ticket = None
                                    else:
                                        self.ticket = random.choice(self.name_list)
                            else:
                                self.ticket_flag = True
                        comment_data.append([timestamp, text, name, name_id])
                        self.old_timestamp = timestamp
            except Exception as e:
                # print(e, samp)
                continue
        # except Exception as e:
        #     # print(e)
        #     pass
        self.old_timestamp = timestamp
        name_list = set(name_list)
        name_list.discard('Alter Ego Project')
        self.name_list = list(name_list)

        now_time = datetime.now()
        now_hour = now_time.hour
        if now_hour in self.random_time:
            # リレータイム：指名orランダムな人が操作権を持つ
            # まずチャット欄の直近5分からランダムに一人選ぶ(何度チャットしていても確率は変わらない)
            # 選ばれた人は 5分間操作ができて、そのticket操作権を誰かに譲渡することもできる
            # 初め30秒間チャットがない場合は再びランダム抽選が行われる
            t_delta = now_time - self.selected_time
            afk_delta = now_time - self.afk_time

            # チケットの失効により誰かに代わる
            if self.ticket is None or t_delta > timedelta(minutes=LIMIT_MIN) or \
                    (self.ticket_flag is False and t_delta > timedelta(seconds=VALIDATE_SEC)) or \
                    (afk_delta > timedelta(seconds=AFK_SEC)):
                if self.ticket_flag is False and t_delta > timedelta(seconds=VALIDATE_SEC):
                    name_list_temp = set(self.name_list)
                    name_list_temp.discard(self.ticket)
                    self.name_list = list(name_list_temp)
                # 代わる人を決める
                if len(self.name_list) > 0:
                    self.ticket = random.choice(self.name_list)

                # 新しいチケット発行
                self.ticket_flag = False
                self.selected_time = datetime.now()
                self.afk_time = datetime.now()
                t_delta = abs(now_time - self.selected_time)
                afk_delta = abs(now_time - self.afk_time)

            if len(self.name_list) == 0:
                self.ticket = None
                msg = 'free play'
            else:
                if self.ticket_flag:
                    msg = '{} さん \nあと {}秒 ({})'.format(
                        self.ticket,
                        int(LIMIT_MIN*60 - t_delta.seconds),
                        int(AFK_SEC - afk_delta.seconds))
                else:
                    msg = '{} さん \n操作チケット {}秒'.format(
                        self.ticket, int(VALIDATE_SEC - t_delta.seconds))
        else:
            # フリータイム：今まで通り
            self.ticket = None
            self.selected_time = datetime.now()
            msg = 'free play'
        # print(msg)
        # print(self.ticket)
        self.ow.set_text('message', msg)
        return comment_data


# import data
# # comment_data.txt にコメントデータを書き込む
# with open("comment_data.txt", mode='w', encoding="utf-8") as f:
#     writer = data.writer(f, lineterminator='\n')
#     writer.writerows(comment_data)

if __name__ == '__main__':
    v = 'iq-CFy-4YYM'
    target_url = 'https://www.youtube.com/live_chat?v=' + v
    gc = GetChat(target_url, 1597150114887955)
    for _ in range(2):
        print([row for row in gc.get()])
    print()