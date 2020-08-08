import numpy as np
import sys
import pyaudio


def check_audio_index():
    CHUNK = 1024 * 2
    RATE = 44100
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16,
                     channels=1,
                     rate=RATE,
                     frames_per_buffer=CHUNK,
                     input=True,
                     output=True)
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        if 'CABLE' in info['name']:
            print(info)


from py.fishing.wav import Wav
class PlotWindow:
    def __init__(self):
        #マイクインプット設定
        self.CHUNK=1024             #1度に読み取る音声のデータ幅
        self.RATE=44100             #サンプリング周波数
        self.RECORD_SECONDS = 0.1
        self.audio=pyaudio.PyAudio()
        self.stream=self.audio.open(format=pyaudio.paInt16,
                                    channels=1,
                                    rate=self.RATE,
                                    input=True,
                                    frames_per_buffer=self.CHUNK)
        self.wav = Wav()

    def update(self):
        # data = np.array([])
        # for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
        #     ret = self.stream.read(self.CHUNK)
        #     ret = np.frombuffer(ret, dtype="int16") / 32768.0
        #     data = np.concatenate([data, ret])
        # vol = int(round(data.max() * 100))
        # print('\r{}      '.format(vol), end='')
        # return vol
        ret = self.stream.read(self.CHUNK)
        ret = np.frombuffer(ret, dtype="int16") / 32768.0
        error = self.wav.is_fishing(ret)
        error = max(0, -int(error/100))
        # print('\r{}      '.format(error)+'\n', end='')
        return error


if __name__=="__main__":
    import connectOBS
    import time, math
    plotwin=PlotWindow()
    plotwin.update()
    ow = connectOBS.ObsWebsket()
    flag_count = 0
    rec_vol = []
    while True:
        vol = plotwin.update()
        # if vol > 5:
        #     vol = 5
        # ow.set_sound_vol(vol)
        if flag_count < 10:
            flag_count += 1
            rec_vol.append(vol)
            time.sleep(0.1)
        elif flag_count == 10:
            ow.set_fish_icon_invisible()
            flag_count += 1
            print("\r " + str(max(rec_vol)) + ' ', end="")
            rec_vol = []
        elif vol > 5:
            flag_count = 0
            ow.set_fish_icon_visible()
            rec_vol.append(vol)
