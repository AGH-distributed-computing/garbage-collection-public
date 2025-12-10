#command.py
from typing import Union

from localization import VerticeLocalization, EdgeLocalization, RubbishBinSide

class MoveToVertice:
    verticeLocalization: VerticeLocalization

class MoveToEdge:
    edgeLocalization: EdgeLocalization

class EmptyBin:
    side: RubbishBinSide

Command = Union[MoveToVertice, MoveToEdge, EmptyBin]