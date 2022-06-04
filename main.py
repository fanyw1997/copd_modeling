from model.patient import Patient
from model.design import Model

def main():
    m = Model(cycle_length = 12,
              time_horizon = 12*50,
              # discount_rate_utility = 0.03,
              # discount_rate_cost: float = 0.03,
              # num_states: int = 5,
    )
    m.add_patients(num_patients = 10)
    for patient in m._patients:
        patient.print()
    # for i in range(m._time_horizon // m._cycle_length):
    #     m.simulate()

if __name__ == '__main__':
    main()


