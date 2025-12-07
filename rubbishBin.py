#rubbishBin.py

from enum import Enum

class RubbishBinType(str, Enum):
    DETACHED_HOUSE = "detached_house"
    APARTMENT_BUILDING = "apartment_building"
    PUBLIC_FACILITY = "public_facility"
    PRODUCTION_PLANT = "production_plant"

    @classmethod
    def from_string(cls, value: str) -> "RubbishBinType":
        try:
            return cls(value)
        except ValueError:
            raise ValueError(
                f"Bin type: '{value}'. "
                f"Does not exist"
            )

class RubbishBin:
    def __init__(self, type, capacity, fillLevel = 0):
        self.type = RubbishBinType.from_string(type)
        self.capacity = capacity #max capacity in litres
        self.fillLevel = fillLevel #current fill level in litres

    def emptyBin(self):
        fillLevel = self.fillLevel
        self.fillLevel = 0
        return fillLevel