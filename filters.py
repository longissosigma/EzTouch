# filters.py
import math

class LowPassFilter:
    def __init__(self, alpha):
        self.__alpha = alpha
        self.__y = None

    def __call__(self, value):
        if self.__y is None:
            self.__y = value
        else:
            self.__y = self.__alpha * value + (1.0 - self.__alpha) * self.__y
        return self.__y

    def set_alpha(self, alpha):
        self.__alpha = alpha

    def get_current(self):
        return self.__y

class OneEuroFilter:
    def __init__(self, freq, min_cutoff=1.0, beta=0.0, d_cutoff=1.0):
        self.__freq = float(freq)
        self.__min_cutoff = float(min_cutoff)
        self.__beta = float(beta)
        self.__d_cutoff = float(d_cutoff)
        self.__x_filter = LowPassFilter(self.__alpha(min_cutoff))
        self.__dx_filter = LowPassFilter(self.__alpha(d_cutoff))
        self.__last_value = None

    def __alpha(self, cutoff):
        tau = 1.0 / (2 * math.pi * cutoff)
        te = 1.0 / self.__freq
        return 1.0 / (1.0 + tau / te)

    def __call__(self, value):
        if self.__last_value is None:
            self.__last_value = value
            return value
        edx = (value - self.__last_value) * self.__freq
        dx = self.__dx_filter(edx)
        cutoff = self.__min_cutoff + self.__beta * abs(dx)
        self.__x_filter.set_alpha(self.__alpha(cutoff))
        self.__last_value = value
        return self.__x_filter(value)

class DualOneEuroFilter:
    def __init__(self, freq, min_cutoff=1.0, beta=0.0, d_cutoff=1.0):
        self.filter_x = OneEuroFilter(freq, min_cutoff, beta, d_cutoff)
        self.filter_y = OneEuroFilter(freq, min_cutoff, beta, d_cutoff)

    def update(self, x, y):
        return self.filter_x(x), self.filter_y(y)