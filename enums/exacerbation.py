from enum import Enum, unique

@unique
class ExacerbationLevels(Enum):
    NONE = 0
    NON_SEVERE = 1
    SEVERE = 2