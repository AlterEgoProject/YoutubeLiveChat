from obswebsocket import obsws, requests
import os

path = os.path.dirname(__file__)
class ObsWebsket:
    def __init__(self):
        host = "localhost"
        port = 4444
        password = ""

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
        ts = ws.ws.call(requests.TakeSourceScreenshot('Aver', embedPictureFormat='jpeg'))
        im = ts.getImg()
        image = Image.open(BytesIO(base64.b64decode(im.replace('data:image/jpeg;base64,', ''))))
        image.show()


if __name__ == '__main__':
    from PIL import Image
    from io import BytesIO
    ws = ObsWebsket()
    ws.now_here(False)
