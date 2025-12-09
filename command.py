#command.py
from typing import Union

from localization import VerticeLocalization, EdgeLocalization, BinLocalization

class MoveToVertice:
    verticeLocalization: VerticeLocalization

class MoveToEdge:
    edgeLocalization: EdgeLocalization

class EmptyBin:
    binLocalization: BinLocalization

Command = Union[MoveToVertice, MoveToEdge, EmptyBin]