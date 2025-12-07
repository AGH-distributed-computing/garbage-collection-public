#localization.py
from typing import Union

class EdgeLocalization:
    def __init__(self, edgeNumber, distanceFromStart):
        self.edgeNumber = edgeNumber
        self.distanceFromStart = distanceFromStart

class VerticeLocalization:
    def __init__(self, verticeNumber):
        self.verticeNumber = verticeNumber

Localization = Union[VerticeLocalization, EdgeLocalization]