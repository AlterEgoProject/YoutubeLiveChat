from py import systems

from obswebsocket import obsws, requests
import os
import numpy as np
import random
import time
import threading

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

        self.image = self.get_snap()
        size = 1920, 1080

        self.sigmoid = lambda x: 1 / (1 + np.exp(-x))
        self.alpha = 0.1
        try:
            self.parameter = np.load('parameter.npy')
        except:
            self.parameter = np.array([
                [1.0, -1.0, -1.0],
                [-1.0, 1.0, -1.0],
                [-1.0, -1.0, 1.0]])
        self.f_str = [
            ['砂浜', 'すなはま'],
            ['草地', 'くさち'],
            ['水', 'みず']]
        self.f = [0.0, 0.0, 0.0]
        self.text = None


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
                crop_range1 = self.extract_image_crop(i, j)[0]
                croped1 = bi_image.crop(crop_range1)
                if np.mean(np.array(croped1)) < image_mean:
                    continue
                if entr_bot < croped1.entropy() < entr_up:
                    crop_range2 = self.extract_image_crop(i, j, padding=50)[0]
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
            self.put_target(x=candidate[max_i][0]*100, y=candidate[max_i][1]*100)
            # plt.imshow(croped, cmap="gray")
        else:
            self.set_icon_invisible('red_target')
        # image.show()
        # print(candidate)

    # 野外にいるか
    def is_field(self):
        self.image = self.get_snap()
        boolean_list = self.detect_map()
        return all(boolean_list)

    # 右下の地図を検知
    def detect_map(self):
        threashold = 200
        map_range = (1520, 745, 1890, 1050)
        croped = self.image.crop(map_range)
        # croped.save('map_2.jpg')
        data = np.asanyarray(croped.convert('L'))
        check_1 = np.mean([data[0], data[-1]]) > threashold
        check_2 = np.mean([data.T[0], data.T[-1]]) > threashold
        check_3 = np.mean(data) < threashold

        return check_1, check_2, check_3

    def light_distribution(self):
        gray_image = self.image.convert('L')
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
        # print(up_left, up_right, bot_left, bot_right)
        return up_left, up_right, bot_left, bot_right

    def draw_color_histogram(self):
        # カラーヒストグラム
        fig = plt.figure()
        ax = plt.axes()
        ax.set_ylim((0, 50000))
        while (1):
            image = self.get_snap()
            upside = image.convert("RGB").crop((0, 0, image.size[0], int(image.size[1] / 2)))
            img = np.array(upside).reshape(-1, 3)
            ax.hist(img, color=["red", "green", "blue"], histtype="step", bins=256)
            plt.pause(1)
            ax.clear()

    def draw_mono_color(self):
        # RGB成分を単離
        fig = plt.figure()
        ax = plt.axes()
        plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
        # plt.axes().set_aspect('equal')
        plt.axis('off')
        while (1):
            image = self.get_snap()
            img = np.array(image)
            plt.imshow(img[:, :, 1], cmap='Greens_r')
            # sns.heatmap(img[:, :, 1], cmap='Greens_r', cbar=False)
            plt.pause(1)

    def adjust_image_position(self, target_x, target_y):
        image_info = self.ws.call(requests.GetSceneItemProperties('Aver'))
        height = image_info.getHeight()
        width = image_info.getWidth()
        source_height = image_info.getSourceheight()
        source_width = image_info.getSourcewidth()
        return target_x * width / source_width, target_y * height / source_height

    # crop_size で分けた時の番地による画像の範囲とOBS上の位置
    def extract_image_crop(self, x_index, y_index, crop_size=(200, 180), padding=(0, 0)):
        crop_range = (
            x_index * crop_size[0] - padding[0],
            y_index * crop_size[1] - padding[1],
            (x_index + 1) * crop_size[0] + padding[0],
            (y_index + 1) * crop_size[1] + padding[1])
        crop_position = self.adjust_image_position(crop_range[0], crop_range[1])
        return crop_range, crop_position

    def put_target(self, x, y):
        adjust_x, adjust_y = self.adjust_image_position(x, y)
        self.ws.call(requests.SetSceneItemPosition('red_target', adjust_x, adjust_y))
        self.set_icon_visible('red_target')

    def put_target_from_index(self, x_index, y_index, crop_size=(200, 180)):
        self.put_target(x_index * crop_size[0], y_index * crop_size[1])

    def set_target_size(self, x, y):
        range = self.adjust_image_position(x, y)
        self.ws.call(requests.SetSceneItemTransform('red_target', range[0] / 201, range[1] / 201, 0))

    def test(self):
        self.image = self.get_snap()
        min_std = 0.1
        best_i = 0
        best_j = 0
        best_mean = []
        std_flag = True
        for j in range(int(self.image.size[1] / 180) * 2 - 1):
            for i in range(int(self.image.size[0] / 200) * 2 - 1):
                # 画面上部は除く
                if 180/2*j < 1080/2:
                    continue
                crop_range = (200/2*i, 180/2*j, 200/2*i + 200, 180/2*j + 180)
                img = np.array(self.image.crop(crop_range))
                temp = [img[:, :, k] / 255 for k in range(3)]
                std = np.max([np.std(np.ravel(im)) for im in temp])
                if std > 0.1:
                    continue
                if std < min_std:
                    min_std = std
                    best_i, best_j = 200/2*i, 180/2*j
                    best_mean = np.array([np.mean(arr) for arr in temp])
                    std_flag = False
        if std_flag:
            return None
        # print(min_std, best_mean)
        self.put_target(best_i, best_j)
        # self.learning.hx(best_mean)
        f = self.sigmoid(np.sum(best_mean * self.parameter, axis=1))
        max_index = np.argmax(f)
        ans = self.show_question(max_index)
        print('question: end!')
        # self.learning.update(best_mean, ans)
        y = np.zeros(3)
        y[max_index] = 1.0
        if ans:
            self.parameter -= self.alpha * (self.parameter * best_mean).T * (self.f - y)
        elif ans is False:
            self.parameter[max_index] -= self.alpha * (self.parameter[max_index] * best_mean).T * (self.f - y)
        else:
            return None
        np.save('parameter', self.parameter)
        return ans

    def show_question(self, index):
        talk_items = ['talk_frame', 'talk_text', 'talk_rubi1', 'talk_rubi2']
        talk_text = '下の赤い場所は\n\n{}であってる？(yes or no)'.format(self.f_str[index][0])
        # print(talk_text)
        self.set_text('talk_text', talk_text)
        self.set_text('talk_rubi2', self.f_str[index][1])
        for name in talk_items:
            self.set_icon_visible(name)
        for i in range(60):
            if self.text is not None:
                for name in talk_items:
                    self.set_icon_invisible(name)
                self.set_icon_invisible('red_target')
                if self.text == 'yes':
                    return True
                elif self.text == 'no':
                    return False
                else:
                    return None
            else:
                time.sleep(1)
                continue
        else:
            print('question: timeout!')
        for name in talk_items:
            self.set_icon_invisible(name)
        self.set_icon_invisible('red_target')
        return None


if __name__ == '__main__':
    self = ObsWebsket()
    learning = systems.Learning()
    while(1):
        self.test()
    print()
    # self.draw_color_histogram()
    # self.draw_mono_color()



# i, j = 5, 5
# crop_range1 = (i * 100, j * 100, (i + 1) * 100, (j + 1) * 100)
# croped1 = image.convert('L').crop(crop_range1)
# crop_range2 = (i * 100 - 50, j * 100 - 50, (i + 1) * 100 + 50, (j + 1) * 100 + 50)
# croped2 = image.convert('L').crop(crop_range2)
# print(np.mean(np.array(croped1)), croped1.entropy(), np.mean(np.array(croped2)), croped2.entropy())
# 140.1847 4.403544215500878 141.138775 4.469934956720045 (23時)

# サイズ調整
# range = self.adjust_image_position(100,100)
# self.ws.call(requests.SetSceneItemTransform('red_target', range[0]/201, range[1]/201, 0))

