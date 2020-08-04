from bs4 import BeautifulSoup
import json
import requests

import time

class GetChat:
    def __init__(self, target_url, old_timestamp=None):
        self.target_url = target_url
        self.comment_data = []
        self.session = requests.Session()
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}

        self.old_timestamp = old_timestamp

    def get(self):
        html = self.session.get(self.target_url, headers=self.headers)
        soup = BeautifulSoup(html.text, "html.parser")

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
        if len(dict_str)==0:
            return []
        dics = eval(dict_str)

        # dics["contents"]["liveChatRenderer"]["actions"]がコメントデータのリスト。
        comment_data = []
        timestamp = self.old_timestamp
        # try:
        for samp in dics["contents"]["liveChatRenderer"]["actions"]:
            try:
                temp = samp['addChatItemAction']['item']['liveChatTextMessageRenderer']
                timestamp = temp['timestampUsec']
                # print(temp['message']['runs'][0]['text'])
                if self.old_timestamp == None or int(self.old_timestamp) < int(timestamp):
                    text = temp['message']['runs'][0]['text']
                    name = temp['authorName']['simpleText']
                    name_id = temp['id']
                    comment_data.append([timestamp, text, name, name_id])
            except Exception as e:
                # print(e, samp)
                continue
        # except Exception as e:
        #     # print(e)
        #     pass
        self.old_timestamp = timestamp
        return comment_data


# import csv
# # comment_data.txt にコメントデータを書き込む
# with open("comment_data.txt", mode='w', encoding="utf-8") as f:
#     writer = csv.writer(f, lineterminator='\n')
#     writer.writerows(comment_data)

if __name__ == '__main__':
    v = '4BE8yy0PAn0'
    target_url = 'https://www.youtube.com/live_chat?v=' + v
    timestamp = None
    gc = GetChat(target_url, timestamp)
    print(gc.get())