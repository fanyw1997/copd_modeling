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


class SimulatorCOPD:
    def __init__(self,
                 cycle_length: int,
                 time_horizon: int,
                 num_individual: int,
                 time_convert: TimeConvert,
                 discount_rate_utility: float = 0.03,
                 discount_rate_cost: float = 0.03
                 ):
        """
        :param cycle_length:            month
        :param time_horizon:            month * cycle number
        """

        # Simulation-related parameters
        self._cycle_length = cycle_length
        self._time_horizon = time_horizon
        self._discount_rate_utility = discount_rate_utility
        self._discount_rate_cost = discount_rate_cost
        self._time_convert = time_convert

        # Initialization-related parameters
        self._num_individual = num_individual

        # Patients setups
        self._reader = AttributeReader()
        self._patients = []

        # Simulation events
        self._screening_strategy_instance = ScreeningStrategy1()
        self._exacerbation_instance = Exacerbation(self._cycle_length)

        # Statistics
        self._result_columns = ['current_month'] + simulator_output_columns

        self._result_df = pd.DataFrame(columns=self._result_columns)
        self._stat_cycle_id = 0
        self._stat_state_counter = [0] * len(State)
        self._stat_detected_state_counter = [0] * len(State)


    def simulate(self):
        self._init(self._num_individual)
        for current_month in tqdm.tqdm(range(0, self._time_horizon, self._cycle_length)):
            self._simulate_one_cycle(current_month)

        self._result_simulation_output('result.csv')

    def _init(self, num_individual: int):
        """
        Each time simulate() is called, _init() will initialize the stats variables and add patient.
        :param num_individual:
        :return:
        """

        self._result_df = pd.DataFrame(columns=self._result_columns)
        self._stat_cycle_id = 0
        self._stat_state_counter = [0] * len(State)
        self._stat_detected_state_counter = [0] * len(State)

        self._add_patients(num_individual, 'initial')



    def _simulate_one_cycle(self, current_month: int):
        self._incidence()
        self._screening(self._screening_strategy_instance, current_month)
        self._treatment()
        self._exacerbation(self._exacerbation_instance)
        self._state_transit()
        self._stat_cycle_id += 1
        self._result_cycle_analysis(current_month)

    def _decrease_state_counter(self, patient: Patient):
        state = patient.get_attribute('state').value
        self._stat_state_counter[state] -= 1
        self._stat_detected_state_counter[state] -= patient.get_attribute('detected').value

    def _increase_state_counter(self, patient: Patient):
        state = patient.get_attribute('state').value
        self._stat_state_counter[state] += 1
        self._stat_detected_state_counter[state] += patient.get_attribute('detected').value

    def _incidence(self):
        self._add_patients(self._incidence_num(), 'incidence')

    def _incidence_num(self):
        return 10

    def _screening(self, scr_strategy: ScreeningStrategy, current_cycle: int):
        for patient in self._patients:
            self._decrease_state_counter(patient)
            scr_strategy.screen(patient, current_cycle)
            self._increase_state_counter(patient)

    def _treatment(self):
        pass

    def _exacerbation(self, exacerbation: Exacerbation):
        for patient in self._patients:
            self._decrease_state_counter(patient)
            exacerbation.exacerbate(patient)
            self._increase_state_counter(patient)

    def _state_transit(self):
        for patient in self._patients:
            self._decrease_state_counter(patient)
            patient.transit()
            self._increase_state_counter(patient)

    def _add_patients(self, num_patients: int = 1, circum: str = 'incidence'):
        assert circum in ['incidence', 'initial'] # 确保circum只能取值incidence或initial
        for i in tqdm.tqdm(range(num_patients)) if circum == 'initial' else range(num_patients):
            patient = Patient()

            # 获取attr生成的顺序，按先后处理patient的各个attr
            for attribute in self._reader.get_attribute_order():
                attribute_parser = self._reader.get_attribute_list()[attribute]
                df = attribute_parser.get_attribute_initial() if circum == 'initial' else attribute_parser.get_attribute_incidence()
                attribute_type = attribute_parser.get_attribute_type()

                depend_attr = df.loc[0]['depend_attr']
                if not depend_attr is None:
                    patient_depend = patient.get_attribute(depend_attr)
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
                if attribute_type == 'integer':
                    lower = df.iloc[target_row]['attr_lower']
                    upper = df.iloc[target_row]['attr_upper']
                    patient.set_attribute_kv(attribute, np.random.randint(lower, upper))
                else:
                    patient.set_attribute_kv(attribute, df.iloc[target_row]['attr_category'])

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