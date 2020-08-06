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

if __name__ == '__main__':
    ws = ObsWebsket()
    ws.now_here(True)