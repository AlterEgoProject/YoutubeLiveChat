from bs4 import BeautifulSoup
import requests

def get_live_url():
    """ 配信URLの自動取得"""
    channel_url = 'https://www.youtube.com/channel/UCKNHDjh8psJwi3G8j6c14mg'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}

    session = requests.Session()
    html = session.get(channel_url, headers=headers)
    soup = BeautifulSoup(html.text, "html.parser")

    try:
        for scrp in soup.find_all("script"):
            if "window[\"ytInitialPlayerResponse\"]" in scrp.text:
                dict_str = scrp.text.split(" = ")[1]
                dict_str = dict_str.replace("false", "False")
                dict_str = dict_str.replace("true", "True")
                dict_str = dict_str.rstrip("  ;\nwindow[\"ytInitialPlayerResponse\"]")
                dics = eval(dict_str)
                temp = dics['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]
                temp = temp['tabRenderer']['content']['sectionListRenderer']['contents'][0]
                temp = temp['itemSectionRenderer']['contents'][0]
                temp = temp['channelFeaturedContentRenderer']['items'][0]
                return temp['videoRenderer']['videoId']
    except:
        pass
    print('配信中のIDを入力')
    return input()