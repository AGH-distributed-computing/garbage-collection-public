#rubbishBin.py
from dataclasses import dataclass
from enum import Enum

from localization import FrozenEdgeLocalization


class RubbishBinType(str, Enum):
    DETACHED_HOUSE = "detached_house"
    APARTMENT_BUILDING = "apartment_building"
    PUBLIC_FACILITY = "public_facility"
    PRODUCTION_PLANT = "production_plant"
    EVENT_DUMP = "event_dump"

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
    def __init__(self, type, capacity, usersCount, fillLevel = 0, isTemporary = False):
        self.type = RubbishBinType.from_string(type)
        self.capacity = capacity #max capacity in litres
        self.usersCount = usersCount
        self.fillLevel = fillLevel #current fill level in litres
        self.alertLevel = None
        self.isTemporary = isTemporary

    def emptyBin(self):
        fillLevel = self.fillLevel
        self.fillLevel = 0
        return fillLevel

    def isAlertLevelExceeded(self):
        if(self.alertLevel is None):
            return False
        if(self.fillLevel > self.capacity*self.alertLevel):
            return True
        return False

#as written in presentation, we don't care what happens with extra garbage after bin is full, so we use mod
    def updateRubbish(self,
                        detached_house_time_series,
                        apartment_building_time_series,
                        public_facility_time_series,
                        production_plant_time_series,
                        series_index
                        ):
        if(self.type == RubbishBinType.DETACHED_HOUSE):
            self.fillLevel += detached_house_time_series[series_index]
        elif(self.type == RubbishBinType.PUBLIC_FACILITY):
            self.fillLevel += public_facility_time_series[series_index]
        elif(self.type == RubbishBinType.PRODUCTION_PLANT):
            self.fillLevel += production_plant_time_series[series_index]
        elif(self.type == RubbishBinType.APARTMENT_BUILDING):
            self.fillLevel += apartment_building_time_series[series_index]

        self.fillLevel %= self.capacity

#this class allows fast add/remove operations
@dataclass(frozen=True)
class AlertBin:
    location: FrozenEdgeLocalization
    side: str