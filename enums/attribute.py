from enum import Enum, unique

@unique
class State(Enum):
    GOLD1 = 0
    GOLD2 = 1
    GOLD3 = 2
    GOLD4 = 3
    COPD_DEATH = 4
    BG_DEATH = 5

@unique
class Sex(Enum):
    MALE = 0
    FEMALE = 1

@unique
class Treatment(Enum):
    F = 0
    T = 1

@unique
class TreatmentMethod(Enum):
    T1 = 0
    T2 = 1

@unique
class Detected(Enum):
    F = 0
    T = 1
