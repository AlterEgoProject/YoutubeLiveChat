# 基底膜のモデル
import numpy as np
import math

class BasilarMembrane:
    #  n # 共振モデルの数
    #  FRAME_RATE # フレームレート
    #  K # 抵抗係数
    #  EIGEN_LIST # 固有振動数の配列

    def __init__(self, target_sec=0.5, k=0.1, frame_rate=44100, chunk=1024):
        self.n = 88
        self.FRAME_RATE = frame_rate
        self.CHUNK = chunk
        self.CHUNK_N = int(frame_rate / chunk * target_sec)
        self.K_ENV = k
        self.DELTA = 1. / frame_rate
        # 共鳴体
        self.x_list = np.zeros(self.n)
        self.v_list = np.zeros(self.n)
        k_list = []
        for i in range(self.n):
            eigen = 27.5 * pow(2, i/13)
            k = pow(2 * math.pi * eigen, 2)
            k_list.append(k)
        self.K_LIST = np.array(k_list)
        self.before_wave = 0

    def oscillate(self, wave):
        before_wave = self.before_wave
        for i in range(self.CHUNK):
            # wave_v = (wave[i]-before_wave) * self.FRAME_RATE
            wave_v = wave[i]
            relative_v = self.v_list - wave_v
            external = - self.K_ENV * np.square(relative_v) * np.sign(relative_v)
            self.v_list += (- self.K_LIST * self.x_list + external) * self.DELTA
            self.x_list += self.v_list * self.DELTA
            before_wave = wave[i]
        return self.mechanical_energy()

    def mechanical_energy(self):
        # 力学的エネルギー
        energy = np.square(self.v_list) / 2 + self.K_LIST * np.square(self.x_list) / 2
        return energy

if __name__ == '__main__':
    frame_rate = 44100
    chunk = 1024
    target_sec = 0.5
    #
    # env_k = 100
    # bm = BasilarMembrane(target_sec, k=env_k, chunk=chunk, frame_rate=frame_rate)

    from matplotlib import pylab as plt
    import scipy.fftpack
    fig, ax = plt.subplots(1, 1)
    # ax.set_ylim((-0.1, 0.1))

    # f0 = 100  # 周波数
    # f1 = 560
    # f2 = 1020
    # sec = 0.01  # 秒

    # t = np.arange(int(chunk))
    # i = 0

    # energy = np.zeros(88)

    import pyaudio
    audio=pyaudio.PyAudio()
    stream=audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=frame_rate,
        input=True,
        frames_per_buffer=chunk)

    N = int(frame_rate / chunk * target_sec)     # FFTのサンプル数
    # hammingWindow = np.hamming(chunk * N)
    hammingWindow = np.hamming(chunk)
    data = np.zeros((N, chunk))

    while(1):
        # i += 1
        # swav = 0.6 * np.sin(2.0 * np.pi * f0 * (t+i*chunk) / frame_rate) \
        # + 0.2 * np.sin(2.0 * np.pi * f1 * (t+i*chunk) / frame_rate)
        # + 0.1 * np.sin(2.0 * np.pi * f2 * (t+i*chunk) / frame_rate)

        # for _ in range(N):
        #     ret = stream.read(chunk)
        #     ret = np.frombuffer(ret, dtype="int16") / 32768.0
        #     data = np.roll(data, chunk)
        #     data[0] = ret
        # windowedData = hammingWindow * np.ravel(data)
        # windowedDFT = np.fft.fft(windowedData)
        # windowedAmp = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in windowedDFT]
        # freqList = np.fft.fftfreq(chunk*N, d=1.0/frame_rate)

        ret = stream.read(chunk)
        data = np.frombuffer(ret, dtype="int16") / 32768.0
        windowedData = hammingWindow * data
        windowedDFT = np.fft.fft(windowedData)
        windowedAmp = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in windowedDFT]
        freqList = np.fft.fftfreq(chunk, d=1.0/frame_rate)

        # line, = ax.plot(np.ravel(windowedData), color='blue')
        line, = ax.plot(freqList, windowedAmp, color='blue')
        ax.axis([0, frame_rate / 2, 0, 10])

        # energy = bm.oscillate(data)
        # diff = 2*energy - np.roll(energy,1) - np.roll(energy,-1)
        # diff[diff<0] = 0
        # line, = ax.plot(bm.x_list, color='blue')
        # line, = ax.plot(energy, color='blue')
        # line, = ax.plot(np.log(energy * 10 + 1), color='blue')
        # line, = ax.plot(np.log(diff[1:-1] + 1), color='blue')
        plt.pause(0.01)
        line.remove()


