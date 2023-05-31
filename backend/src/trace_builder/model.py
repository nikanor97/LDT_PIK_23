from dataclasses import dataclass


@dataclass
class Point:
    x: float
    y: float


@dataclass
class Segment:
    start: Point
    end: Point
    length: float = None
