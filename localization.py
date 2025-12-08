#localization.py
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

class VerticeLocalization:
    def __init__(self, verticeNumber):
        self.verticeNumber = verticeNumber

Localization = Union[VerticeLocalization, EdgeLocalization]