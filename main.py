from model.sim_copd import SimulatorCOPD
from utils.time_convert import TimeConvert


def main():
    tc = TimeConvert(2022, 6)
    m = SimulatorCOPD(cycle_length = 12,
                      time_horizon = 12*50,
                      num_individual = 1000,
                      time_convert = tc,
                      )
    m.simulate()

if __name__ == '__main__':
    main()


