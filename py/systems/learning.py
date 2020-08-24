import numpy as np

class Learning:
    def __init__(self):
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

    def hx(self, best_mean):
        self.f = self.sigmoid(np.sum(best_mean * self.parameter, axis=1))

    def update(self, best_mean, ans):
        max_index = np.argmax(self.f)
        y = np.zeros(3)
        y[max_index] = 1.0
        if ans:
            self.parameter -= self.alpha * (self.parameter * best_mean).T * (self.f - y)
        else:
            self.parameter[max_index] -= self.alpha * (self.parameter[max_index] * best_mean).T * (self.f - y)
        np.save('parameter', self.parameter)
