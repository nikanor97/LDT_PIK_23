from dataclasses import dataclass
from typing import Tuple

@dataclass
class Point:
    x: float
    y: float


@dataclass
class Segment:
    start: Point
    end: Point
    length: float = None

class DXFStuff:
    id: int
    name: str
    coordinates: Point
    height: float = None