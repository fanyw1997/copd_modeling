import numpy as np

class Patient:
    """
    1.  给Patient加上性别和年龄
    2.  get_trans_prob函数概率基于患者性别和年龄
    3.  生成患者时，年龄和性别比例
    """

    def __init__(self, **kwargs):
        self._num_states = 5
        self._state = 0
        self.set_attributes(**kwargs)

    def set_attributes(self, **kwargs):
        for k, v in kwargs:
            self.__dict__[k] = v

    def get_attribute(self, k: str):
        return self.__dict__[k]

    def get_trans_prob(self):
        return np.array([[0.9047, 0.0876, 0, 0, 0.0077],
                         [0.0510, 0.9001, 0.0362, 0, 0.0128],
                         [0, 0.1044, 0.8368, 0.0324, 0.0265],
                         [0, 0, 0.0936, 0.8187, 0.0877],
                         [0, 0, 0, 0, 1]])

    def transit(self):
        temp_random = float(np.random.random())
        temp_prob = self.get_trans_prob()
        temp_sum = 0

        target = None
        for i in range(self._num_states):
            temp_sum += temp_prob[self._state][i]
            if temp_sum > temp_random:
                target = i
                break

        self._state = target
        return target

    def print(self):
        print(self.__dict__)