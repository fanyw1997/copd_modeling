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

    def add_patients(self, num_patients: int = 1):
        for i in range(num_patients):
            self._patients.append(Patient())

    def simulate(self):
        temp_states_count = [0] * self._num_states
        for patient in self._patients:
            state = patient.transit()
            temp_states_count[state] += 1
        print(temp_states_count)
