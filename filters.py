# Chứa thuật toán lọc nhiễu (Moving Average)

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


class OneEuroFilter:
    """
    Thuật toán lọc nhiễu thích ứng 1€ Filter: Triệt tiêu rung lắc tần số cao
    khi đứng yên nhưng giảm độ trễ tối đa khi di chuyển nhanh.
    """
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

        # Tính toán vận tốc thay đổi tọa độ
        edx = (value - self.__last_value) * self.__freq
        cutoff_d = self.__d_cutoff
        dx = self.__dx_filter(edx)
        
        # Thay đổi tần số cắt thích ứng theo vận tốc tuyệt đối
        cutoff = self.__min_cutoff + self.__beta * abs(dx)
        self.__x_filter.set_alpha(self.__alpha(cutoff))
        
        self.__last_value = value
        return self.__x_filter(value)


class DualOneEuroFilter:
    """Bọc 2 bộ lọc OneEuro độc lập cho trục X và trục Y."""
    def __init__(self, freq, min_cutoff=1.0, beta=0.0, d_cutoff=1.0):
        self.filter_x = OneEuroFilter(freq, min_cutoff, beta, d_cutoff)
        self.filter_y = OneEuroFilter(freq, min_cutoff, beta, d_cutoff)

    def update(self, x, y):
        smooth_x = self.filter_x(x)
        smooth_y = self.filter_y(y)
        return smooth_x, smooth_y