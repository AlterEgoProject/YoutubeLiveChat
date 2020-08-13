from obswebsocket import obsws, requests
import os
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

from io import BytesIO

path = os.path.dirname(__file__)
class ObsWebsket:
    def __init__(self):
        host = "localhost"
        port = 4444
        password = "password"

        self.ws = obsws(host, port, password)
        self.ws.connect()

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
        file = path + '/image/vol_{}.png'.format(str(vol))
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
        import base64
        while(1):
            ts = self.ws.call(requests.TakeSourceScreenshot('Aver', embedPictureFormat='jpeg'))
            im = ts.getImg()
            image = Image.open(BytesIO(base64.b64decode(im.replace('data:image/jpeg;base64,', ''))))

            threshold = 200
            gray_image = image.convert('L')
            bi_image = gray_image.point(lambda x: 0 if x < threshold else 255)
            im_size = bi_image.size

            entr_bot = 0.03
            entr_up = 0.1

            # fig = plt.figure()
            # ax = plt.axes()
            # ax.imshow(bi_image)

            candidate = []
            i_index = int(im_size[0] / 100)
            j_index = int(im_size[1] / 100)
            for i in range(1, i_index - 1):
                for j in range(1, j_index - 1):
                    crop_range1 = (i * 100, j * 100, (i + 1) * 100, (j + 1) * 100)
                    croped1 = bi_image.crop(crop_range1)
                    if entr_bot < croped1.entropy() < entr_up:
                        crop_range2 = (i * 100 - 50, j * 100 - 50, (i + 1) * 100 + 50, (j + 1) * 100 + 50)
                        croped2 = bi_image.crop(crop_range2)
                        if croped1.entropy() > croped2.entropy():
                            candidate.append((i, j, croped1.entropy(), croped2.entropy()))
                            # r = patches.Rectangle(xy=(100*i, 100*j), width=100, height=100, ec='r', fill=False)
                            # ax.add_patch(r)

            self.ws.call(requests.SetSceneItemProperties('red_target', position_x=100.0))
            image.show()
            print()


if __name__ == '__main__':
    os = ObsWebsket()
    os.get_snap()
    os.now_here(False)
