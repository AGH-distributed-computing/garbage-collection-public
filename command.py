#command.py
from typing import Union

from localization import VerticeLocalization, EdgeLocalization


class MoveToVertice:
    vertice: VerticeLocalization

class MoveToEdge:
    edge: EdgeLocalization

class EmptyBin:
    edge: EdgeLocalization

Command = Union[MoveToVertice, MoveToEdge, EmptyBin]