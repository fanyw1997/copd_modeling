import numpy as np

from model.patient import Patient

class ScreeningMethod:
    # Methods定义了sensitivity, specificity以及population
    def __init__(self):
        self._sensitivity = 0
        self._specificity = 0

    def screen(self, patient: Patient):
        pass

class ScreeningMethod1(ScreeningMethod):
    def __init__(self):
        super().__init__()
        self._sensitivity = 0.9
        self._specificity = 0.9

    def screen(self, patient: Patient):
        age = patient.get_attribute('age')
        detected = patient.get_attribute('detected')
        if age > 40 and not detected:
            if float(np.random.random()) <= self._sensitivity:
                patient.set_attributes(detected=True)

from parameters.consts import screening_strategy_1_month_method

class ScreeningStrategy:
    # Strategy定义了screening的时间和对应的method
    def __init__(self, month_method: dict):
        """
        :param month_method: k, v:
            k:  which cycle
            v:  which method, ScreeningMethod()
        """
        self._month_method = month_method

    def screen(self, patient: Patient, current_month: int):
        if current_month in self._month_method:
            self._month_method[current_month].screen(patient)

class ScreeningStrategy1(ScreeningStrategy):
    def __init__(self):
        super().__init__(screening_strategy_1_month_method)
