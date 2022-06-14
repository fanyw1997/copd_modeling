import numpy as np
import pandas as pd
import tqdm

from enums.attribute import State
from model.exacerbation import Exacerbation
from model.patient import Patient
from model.screening import ScreeningStrategy, ScreeningStrategy1
from utils.read_patient_attributes import AttributeReader
from parameters.consts import simulator_output_columns
from utils.time_convert import TimeConvert

class Model:
    def __init__(self,
                 cycle_length: int,
                 time_horizon: int,
                 discount_rate_utility: float = 0.03,
                 discount_rate_cost: float = 0.03,
                 num_states: int = 5,
                 ):
        self._cycle_length = cycle_length
        self._time_horizon = time_horizon
        self._discount_rate_utility = discount_rate_utility
        self._discount_rate_cost = discount_rate_cost
        self._num_states = num_states
        self._patients = []
        self._reader = Reader()

    def add_patients(self, num_patients: int = 1, circum: str = 'incidence'):
        assert circum in ['incidence', 'initial'] # 确保circum只能取值incidence或initial
        for i in range(num_patients):
            patient = Patient()

            # 获取attr生成的顺序，按先后处理patient的各个attr
            for attr in self._reader.get_attributes_order():
                attr_reader = self._reader.get_attributes()[attr]
                df = attr_reader.get_initial() if circum == 'initial' else attr_reader.get_incidence()
                attr_type = attr_reader.get_attr_type()

                depend_key = df.loc[0]['depend_key']
                if not depend_key is None:
                    patient_depend = patient.get_attribute(depend_key)
                    df = df[df['depend_value'] == patient_depend]

                # 根据input的分布给patient随机分配该attr的值
                temp_random = float(np.random.random())
                temp_sum = 0
                target_row = None # 通过随机摇色得到该patient所对应的attr_value行号

                for i in range(len(df)):
                    temp_sum += df.iloc[i]['attr_value']

                    if temp_sum >= temp_random:
                        target_row = i
                        break
                if attr_type == 'integer':
                    lower = df.iloc[target_row]['attr_lower']
                    upper = df.iloc[target_row]['attr_upper']
                    patient.__dict__[attr] = np.random.randint(lower, upper)
                else:
                    patient.__dict__[attr] = df.iloc[target_row]['attr_category']

            self._patients.append(patient)
            self._increase_state_counter(patient)

    def _result_cycle_analysis(self, current_month: int):
        """
        Collect all the information per cycle
        :return:
        """
        result_df = self._result_df

        # Make sure that at the end of this function, each value in the result dict is filled (not None)
        result_dict = {k: None for k in self._result_columns}
        result_dict['current_month'] = current_month

        result_dict['cycle_id'] = self._stat_cycle_id
        result_dict['real_year'], result_dict['real_month'] = \
            self._time_convert.get_real_year_month(current_month)

        result_dict['num_patient_gold1'] = self._stat_state_counter[State.GOLD1.value]
        result_dict['num_patient_gold2'] = self._stat_state_counter[State.GOLD2.value]
        result_dict['num_patient_gold3'] = self._stat_state_counter[State.GOLD3.value]
        result_dict['num_patient_gold4'] = self._stat_state_counter[State.GOLD4.value]
        result_dict['num_patient_copd_death'] = self._stat_state_counter[State.COPD_DEATH.value]
        result_dict['num_patient_bg_death'] = self._stat_state_counter[State.BG_DEATH.value]
        result_dict['num_patient_alive_sum'] = sum(self._stat_state_counter[State.GOLD1.value: State.GOLD4.value + 1])

        result_dict['num_patient_detected_gold1'] = self._stat_detected_state_counter[State.GOLD1.value]
        result_dict['num_patient_detected_gold2'] = self._stat_detected_state_counter[State.GOLD2.value]
        result_dict['num_patient_detected_gold3'] = self._stat_detected_state_counter[State.GOLD3.value]
        result_dict['num_patient_detected_gold4'] = self._stat_detected_state_counter[State.GOLD4.value]
        result_dict['num_patient_detected_sum'] = sum(self._stat_detected_state_counter[State.GOLD1.value: State.GOLD4.value + 1])

        for k, v in result_dict.items():
            if v is None:
                raise Exception(f'Key {k} is None, check again.')

        result_df.loc[len(result_df)] = [result_dict[col] for col in self._result_columns]

    def _result_simulation_output(self, filename: str):
        self._result_df.sort_values(by='cycle_id', inplace=True)
        self._result_df.to_csv(filename, index=False, float_format='%.3f')