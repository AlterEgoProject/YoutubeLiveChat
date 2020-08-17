import numpy as np
import pyaudio
import wave
import threading
import time

from py.systems import connectOBS
from py.fishing.wav import Wav


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


class PlotWindow:
    def __init__(self, ps=None):
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
        self.flag_count = 0
        self.rec_vol = []
        self.ow = connectOBS.ObsWebsket()
        self.average_vol = 0
        self.ps = ps

    def start(self):
        self.update()
        while True:
            vol = self.update()
            if vol > 5:
                vol = 5
            self.ow.set_sound_vol(vol)
            continue

    def update(self):
        data = np.array([])
        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            ret = self.stream.read(self.CHUNK)
            ret = np.frombuffer(ret, dtype="int16") / 32768.0
            data = np.concatenate([data, ret])
        vol = np.abs(data.max(initial=0))
        self.average_vol = vol / 500 + self.average_vol * 499/500
        # print('\r{}      '.format(vol), end='')
        return int(vol / self.average_vol)

    def record(self):
        frames = []
        avoid = 0
        try:
            while(1):
                data = self.stream.read(self.CHUNK)
                frames.append(data)
                avoid += 1
                if avoid > pow(10, 4):
                    frames = []
                    print('break record loop')
                    break
        except KeyboardInterrupt:
            print(len(frames))
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()

            import datetime
            import os
            now = datetime.datetime.now()
            output_path = 'py/fishing/record/{0:%Y%m%d_%H%M%S}.wav'.format(now)

            wf = wave.open(output_path, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))
            wf.close()

    def fishing(self):
        t = threading.currentThread()
        initial_val = 0
        before_val = 0
        for i in range(int(self.RATE/self.CHUNK * 60)):
            data = self.stream.read(self.CHUNK)
            chunk_val = np.sum(np.abs(np.frombuffer(data, dtype="int16") / 32768.0))
            val = chunk_val + before_val
            before_val = chunk_val
            if i < (self.RATE/self.CHUNK*3):
                if val > initial_val * 0.8:
                    initial_val = val
            else:
                if val > initial_val:
                    print('fishing: hit!')
                    self.ps.press_key('a')
                    self.ow.set_icon_visible('fish')
                    time.sleep(0.5)
                    break
            if getattr(t, "do_run", False):
                print('fishing: terminate!')
                break
        else:
            print('fishing: timeout!')
            self.ps.press_key('a')
        self.ow.set_icon_invisible('fish')


if __name__ == "__main__":
    plotwin = PlotWindow()
    plotwin.start()
