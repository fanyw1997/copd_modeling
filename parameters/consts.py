from enums.exacerbation import ExacerbationLevels
from enums.attribute import State

"""
parameters related to exacerbation
"""
exacerbation_annual_rate = {
    State.GOLD1: {
        ExacerbationLevels.NON_SEVERE: 0.4,
        ExacerbationLevels.SEVERE: 0.0,
    },
    State.GOLD2: {
        ExacerbationLevels.NON_SEVERE: 0.74,
        ExacerbationLevels.SEVERE: 0.11,
    },
    State.GOLD3: {
        ExacerbationLevels.NON_SEVERE: 1.09,
        ExacerbationLevels.SEVERE: 0.25,
    },
    State.GOLD4: {
        ExacerbationLevels.NON_SEVERE: 1.46,
        ExacerbationLevels.SEVERE: 0.54,
    },
}
exacerbation_severe_mortality_prob = {
    State.GOLD1: 0.01,
    State.GOLD2: 0.02,
    State.GOLD3: 0.03,
    State.GOLD4: 0.04,
}

"""
columns contained in the output file
"""
simulator_output_columns = [
    'cycle_id',
    'real_year',
    'real_month',

    'num_patient_gold1',
    'num_patient_gold2',
    'num_patient_gold3',
    'num_patient_gold4',
    'num_patient_copd_death',
    'num_patient_bg_death',
    'num_patient_alive_sum',

    'num_patient_detected_gold1',
    'num_patient_detected_gold2',
    'num_patient_detected_gold3',
    'num_patient_detected_gold4',
    'num_patient_detected_sum',

]

"""
screening strategy decision: choose which strategy
screening strategy: at which simulation month, use what method
"""
from model.screening import ScreeningMethod1
screening_strategy_1_month_method = {
    5 * 12: ScreeningMethod1(),
    10 * 12: ScreeningMethod1()
}

from model.screening import ScreeningStrategy1
screening_strategy_decision = ScreeningStrategy1()