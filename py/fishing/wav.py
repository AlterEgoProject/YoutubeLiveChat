import wave
import numpy as np
import matplotlib.pyplot as plt # 波形見るとき使う
from matplotlib.pyplot import *
import pyaudio # 鳴らすとき使う
import struct # バイナリデータを扱うとき使う
import csv


# 'rb'で読み込みモード
def extract(i):
    wf = wave.open('{}.wav'.format(i), mode='rb')
    # print('type: ', type(wf))

    wf.rewind() # ポインタを先頭に戻す
    buf = wf.readframes(-1) # 全部読み込む

    data = []
    # 2なら16bit，4なら32bitごとに10進数化
    if wf.getsampwidth() == 2:
        data = np.frombuffer(buf, dtype='int16')
    elif wf.getsampwidth() == 4:
        data = np.frombuffer(buf, dtype='int32')

    # ステレオの場合，チャンネルを分離
    if wf.getnchannels()==2:
        data_l = data[::2] / 32768.0
        data_r = data[1::2] / 32768.0
        # plt.subplot(211)
        # plt.plot(data_l)
        # plt.subplot(212)
        # plt.plot(data_r)
        # plt.show()
        return [data_l, data_r]
    else:
        # plt.plot(data)
        # plt.show()
        return [data / 32768.0]


def find_peak(data):
    index = np.argmax(np.arange(len(data), 0, -1) * data)
    return data[index-1024:index+1024*8]
    # return data[index-1024:index+1024*7]


def fft_proccess(data):
    hammingWindow = np.hamming(1024)
    windowedData = hammingWindow * data
    windowedDFT = np.fft.fft(windowedData)
    windowedAmp = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in windowedDFT]
    freqList = np.fft.fftfreq(1024, d=1.0 / 44100)
    return windowedAmp

import random
def step1():
    freqList = np.fft.fftfreq(1024, d=1.0 / 44100)
    for j in range(8):
        rows = []
        for i in range(1, 8):
            origin = extract(i)
            for data in origin:
                data = find_peak(data)
                for _ in range(50):
                    ra = random.randint(0, 1023)
                    selected_data = data[j * 1024 + ra:(j + 1) * 1024 + ra]
                    # plot(selected_data)
                    amp = fft_proccess(selected_data)
                    rows.append(list(amp))
                    # plot(freqList, amp)
        # with open('data/amp_{}.csv'.format(j), 'w', newline="") as f:
        #     writer = csv.writer(f)
        #     writer.writerows(rows)

        # axis([0, 44100 / 2, 0, 10])
        show()


def step2():
    for j in range(14):
        rows = []
        with open('data/amp_{}.csv'.format(j)) as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) > 0:
                    rows.append(row)
            print()


corr = [
    0.6934795217296021, 0.9010272403395447, 0.8218618088285979, 0.7305615159309644,
    0.7702691075812407, 0.686291474071018, 0.6395189384176889, 0.6657439882519212
]


import os
class Wav:
    def __init__(self):
        base_path = os.path.dirname(__file__)
        self.param = np.loadtxt(base_path + '/parameter.csv', delimiter=",", dtype=float)
        self.before_err = np.sum(np.square(self.param))
        self.data = np.zeros((8, 1024))

    def is_fishing(self, ret):
        amp = np.array(fft_proccess(ret))
        self.data = np.roll(self.data, 1, axis=0)
        self.data[0] = amp
        err = np.square(self.param - self.data)
        err = np.array([corr[i] * err[i] for i in range(8)])
        diff = self.before_err - np.sum(err)
        self.before_err = np.sum(err)
        return diff

def cal_error():
    len_n = 1
    split_n = 1
    param = np.loadtxt('parameter.csv', delimiter=",", dtype=float)
    # param = np.array([corr[i] * param[i] for i in range(8)])
    param = np.split(param, len_n, 0)[0]
    param = np.split(param, split_n, 1)[0]
    before_diff = np.sum(np.square(param))
    err_list = []
    for i in range(1, int(8/len_n)):
        origin = extract(i)
        for o in origin:
            data = np.zeros((int(8/len_n), int(1024/split_n)))
            temp = []
            for j in range(int(len(o)/1024)):
                output = o[j * 1024:(j + 1) * 1024]
                amp = np.array(fft_proccess(output))
                amp = np.split(amp, split_n, 0)[0]
                data = np.roll(data, 1, axis=0)
                data[0] = amp
                # plot(np.ravel(data))
                # plot(np.ravel(param))
                # show()
                err = np.square(param - data)
                err = np.array([corr[i] * err[i] for i in range(8)])
                err = np.sum(err)
                # plot(err)
                # show()
                temp.append(before_diff - err)
                before_diff = err
            # err_list.append(temp)
            plot(temp)
        show()


# cal_error()