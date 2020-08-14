from obswebsocket import obsws, requests
import os
import numpy as np
import random

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageStat

from io import BytesIO
import base64

path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class ObsWebsket:
    def __init__(self):
        host = "localhost"
        port = 4444
        password = ""

        self.ws = obsws(host, port, password)
        self.ws.connect()
        size = 1920, 1080



    def now_here(self, msg):
        if msg:
            # file = path + 'here.png'
            self.ws.call(requests.SetSceneItemProperties('here', visible=True))
            self.ws.call(requests.SetSceneItemProperties('leave', visible=False))
        else:
            # file = path + 'leave.png'
            self.ws.call(requests.SetSceneItemProperties('here', visible=False))
            self.ws.call(requests.SetSceneItemProperties('leave', visible=True))
        # self.ws.call(requests.SetSourceSettings('now_icon', sourceSettings={'file': file}))

    def set_sound_vol(self, vol):
        # vol = 0~5
        file = path + '\\image\\vol_{}.png'.format(str(vol))
        self.ws.call(requests.SetSourceSettings('sound', sourceSettings={'file': file}))

    def set_fish_icon_visible(self):
        # file = path +'simple_fish.png'
        self.ws.call(requests.SetSceneItemProperties('fish', visible=True))

    def set_fish_icon_invisible(self):
        # file = path +'simple_fish.png'
        self.ws.call(requests.SetSceneItemProperties('fish', visible=False))

    def set_text(self, name, msg):
        self.ws.call(requests.SetSourceSettings(name, {'text': msg}))

    def get_snap(self):
        ts = self.ws.call(requests.TakeSourceScreenshot('Aver', embedPictureFormat='jpeg'))
        im = ts.getImg()
        image = Image.open(BytesIO(base64.b64decode(im.replace('data:image/jpeg;base64,', ''))))
        return image

    def set_icon_visible(self, name):
        self.ws.call(requests.SetSceneItemProperties(name, visible=True))

    def set_icon_invisible(self, name):
        self.ws.call(requests.SetSceneItemProperties(name, visible=False))

    def detect_clam(self, image):
        gray_image = image.convert('L')
        hist = gray_image.histogram()

        s = 0
        i = 0
        half = sum(hist) / 2
        for val in hist:
            s += val
            if s > half:
                half_i = i
                break
            i += 1
        else:
            half_i = 200

        threshold = half_i
        entr_bot = 0.02
        entr_up = 0.05

        image_mean = np.mean(np.asarray(gray_image))
        bi_image = gray_image.point(lambda x: 0 if x < threshold else 255)
        im_size = bi_image.size

        # fig = plt.figure()
        # ax = plt.axes()
        # ax.imshow(gray_image, cmap = "gray")

        candidate = []
        i_index = int(im_size[0] / 100)
        j_index = int(im_size[1] / 100)
        for i in range(1, i_index - 1):
            for j in range(1, j_index - 1):
                crop_range1 = (i * 100, j * 100, (i + 1) * 100, (j + 1) * 100)
                croped1 = bi_image.crop(crop_range1)
                if np.mean(np.array(croped1)) < image_mean:
                    continue
                if entr_bot < croped1.entropy() < entr_up:
                    crop_range2 = (i * 100 - 50, j * 100 - 50, (i + 1) * 100 + 50, (j + 1) * 100 + 50)
                    croped2 = bi_image.crop(crop_range2)
                    if croped1.entropy() > croped2.entropy():
                        candidate.append((i, j, crop_range1, croped1.entropy(), croped2.entropy()))
                        # r = patches.Rectangle(xy=(100*i, 100*j), width=100, height=100, ec='r', fill=False)
                        # ax.add_patch(r)
        if len(candidate) > 0:
            max_mean = 0
            max_i = 0
            crop_range1 = None
            ent = 0
            for i in range(len(candidate)):
                sum_croped = np.mean(np.asarray(candidate[i][2]))
                if max_mean < sum_croped:
                    max_mean = sum_croped
                    max_i = i
                    crop_range1 = np.mean(np.asarray(gray_image.crop(candidate[i][2])))
                    ent = round(candidate[i][3], 4)
            print('\navr:{}, thr:{}, ent:{}'.format(int(crop_range1), threshold, ent))
            self.ws.call(requests.SetSceneItemPosition('red_target', x=candidate[max_i][0]*100, y=candidate[max_i][1]*100))
            self.set_icon_visible('red_target')
            # plt.imshow(croped, cmap="gray")
        else:
            self.set_icon_invisible('red_target')
        # image.show()
        # print(candidate)

    # 野外にいるか
    def is_field(self):
        image = self.get_snap()
        boolean_list = self.detect_map(image)
        return all(boolean_list)

    # 右下の地図を検知
    def detect_map(self, image):
        threashold = 200
        map_range = (1520, 745, 1890, 1050)
        croped = image.crop(map_range)
        # croped.save('map_2.jpg')
        data = np.asanyarray(croped.convert('L'))
        check_1 = np.mean([data[0], data[-1]]) > threashold
        check_2 = np.mean([data.T[0], data.T[-1]]) > threashold
        check_3 = np.mean(data) < threashold

        return check_1, check_2, check_3

    def light_distribution(self, image):
        gray_image = image.convert('L')
        im_size = gray_image.size
        arr = np.array(gray_image)
        up_bot = np.array_split(arr, 2, 0)
        up_split = [np.mean(arr) for arr in np.array_split(up_bot[0], 2, 1)]
        bot_split = [np.mean(arr) for arr in np.array_split(up_bot[1], 2, 1)]
        s = np.sum([up_split, bot_split])
        up_left = round(up_split[0]/s, 2)
        up_right = round(up_split[1]/s, 2)
        bot_left = round(bot_split[0]/s, 2)
        bot_right = round(bot_split[1]/s, 2)
        return up_left, up_right, bot_left, bot_right


if __name__ == '__main__':
    self = ObsWebsket()
    fig = plt.figure()
    ax = plt.axes()
    ax.set_ylim((0, 50000))
    for _ in range(10):
        image = self.get_snap()
        # line1, = ax.plot(image.convert('L').histogram(), color='gray')
        upside = np.asarray(image.convert("RGB")).
        img = np.asarray(image.convert("RGB")).reshape(-1, 3)
        ax.hist(img, color=["red", "green", "blue"], histtype="step", bins=256)
        plt.pause(1)
        ax.clear()
    print(self.light_distribution(image))

# i, j = 5, 5
# crop_range1 = (i * 100, j * 100, (i + 1) * 100, (j + 1) * 100)
# croped1 = image.convert('L').crop(crop_range1)
# crop_range2 = (i * 100 - 50, j * 100 - 50, (i + 1) * 100 + 50, (j + 1) * 100 + 50)
# croped2 = image.convert('L').crop(crop_range2)
# print(np.mean(np.array(croped1)), croped1.entropy(), np.mean(np.array(croped2)), croped2.entropy())
# 140.1847 4.403544215500878 141.138775 4.469934956720045 (23時)