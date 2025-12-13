#localization.py
from enum import Enum
from typing import Union

class EdgeLocalization:
    def __init__(self, edgeNumber, distanceFromStart):
        self.edgeNumber = edgeNumber
        self.distanceFromStart = distanceFromStart

        def __eq__(self, other):
            if not isinstance(other, EdgeLocalization):
                return NotImplemented
            if(self.edgeNumber == other.edgeNumber and self.distanceFromStart == other.distanceFromStart):
                return True
            return False

    def calculateDistance(self, EdgeLocalization):
        return EdgeLocalization.distanceFromStart - self.distanceFromStart

class VerticeLocalization:
    def __init__(self, verticeNumber):
        self.verticeNumber = verticeNumber

class RubbishBinSide(str, Enum):
    LEFT = "left"
    RIGHT = "right"

    @classmethod
    def from_string(cls, value: str) -> "RubbishBinSide":
        try:
            return cls(value)
        except ValueError:
            raise ValueError("Side must be either left or right!")

    def to_string(self) -> str:
        return self.value

Localization = Union[VerticeLocalization, EdgeLocalization]