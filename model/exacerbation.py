import numpy as np
import math

from enums.attribute import State
from enums.exacerbation import ExacerbationLevels
from model.patient import Patient
from model.screening import ScreeningMethod
from parameters.consts import exacerbation_annual_rate, exacerbation_severe_mortality_prob


class Exacerbation:
    def __init__(self, cycle_length: int):
        self._annual_rate = exacerbation_annual_rate
        self._severe_mortality_prob = exacerbation_severe_mortality_prob
        self._cycle_length = cycle_length

    def exacerbate(self, patient: Patient):
        patient.set_attributes(exacerbation=ExacerbationLevels.NONE)
        state = patient.get_attribute('state')
        if state in self._annual_rate:

            annual_rate_non_severe = self._annual_rate[state][ExacerbationLevels.NON_SEVERE]
            annual_rate_severe = self._annual_rate[state][ExacerbationLevels.SEVERE]

            prob_exacerbation_non_severe = 1 - math.exp( - annual_rate_non_severe * self._cycle_length / 12)
            prob_exacerbation_severe = 1 - math.exp(- annual_rate_severe * self._cycle_length / 12)
            prob_exacerbation_severe_mortality = self._severe_mortality_prob[state]

            if float(np.random.random()) <= prob_exacerbation_non_severe:
                patient.set_attributes(exacerbation=ExacerbationLevels.NON_SEVERE)
            # 假设一个cycle内即发生severe又non-severe时，将exacerbation-level设为severe

            if float(np.random.random()) <= prob_exacerbation_severe:
                patient.set_attributes(exacerbation=ExacerbationLevels.SEVERE)

                if float(np.random.random()) <= prob_exacerbation_severe_mortality:
                    patient.set_attributes(state=State.COPD_DEATH)

