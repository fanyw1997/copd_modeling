from model.patient import Patient

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
                else:
                    pass

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

    def simulate(self):
        temp_states_count = [0] * self._num_states
        for patient in self._patients:
            state = patient.transit()
            temp_states_count[state] += 1
        print(temp_states_count)
