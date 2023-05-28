from collections.abc import Iterable
from typing import List, Tuple

from model import Point, Segment


def coordinate2point(coordinate: Tuple[float, float]) -> Point:
    if isinstance(coordinate, Iterable) and len(coordinate) == 2:
        return Point(coordinate[0], coordinate[1])
    else:
        raise ValueError("coordinate should be Itearable and have len == 2")


def point2coordinate(point: Point) -> Tuple[float, float]:
    return (point.x, point.y)


def coordinates2segments(segments: List[Tuple[Tuple[float, float]]]) -> List[Segment]:
    final_segments = []
    for segment in segments:
        if isinstance(segment[0], Iterable):
            new_segment = Segment(
                Point(segment[0][0], segment[0][1]), Point(segment[1][0], segment[1][1])
            )
        elif isinstance(segment[0], Point):
            new_segment = Segment(segment[0], segment[1])
        else:
            raise ValueError(
                "Point in segment should be Iterable or Tuple(float, float)"
            )
        final_segments.append(new_segment)
    return final_segments


def coordinates2segment(segment: Tuple[Tuple[float, float]]) -> Segment:
    if isinstance(segment[0], Iterable):
        return Segment(
            Point(segment[0][0], segment[0][1]), Point(segment[1][0], segment[1][1])
        )
    elif isinstance(segment[0], Point):
        return Segment(segment[0], segment[1])
    else:
        raise ValueError("Point in segment should be Iterable or Tuple(float, float)")


def segments2coordinates(segments: List[Segment]) -> List[Tuple[Tuple[float, float]]]:
    final_segments = []
    for segment in segments:
        final_segments.append(
            ((segment.start.x, segment.start.y), (segment.end.x, segment.end.y))
        )
    return final_segments


def segment2coordinates(segment: Segment) -> Tuple[Tuple[float, float]]:
    return ((segment.start.x, segment.start.y), (segment.end.x, segment.end.y))
