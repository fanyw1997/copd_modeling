from enum import EnumMeta

from .attribute import State as state
from .attribute import Sex as sex
from .attribute import Treatment as treatment
from .attribute import TreatmentMethod as treatment_method
from .attribute import Detected as detected

def get_enum_class(attr: str):
    glob = globals()

    if attr in glob and type(glob[attr]) == EnumMeta:
        return glob[attr]
    raise Exception(f'No such enum type: {attr}')

def get_enum_element(attr: str, value: str):
    enum_class = get_enum_class(attr)

    if value in enum_class.__members__:
        return enum_class.__members__[value]
    raise Exception(f'{value} is not in enumerate class {attr}.')
