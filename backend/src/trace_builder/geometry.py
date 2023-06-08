from typing import List

import numpy as np
from src.trace_builder.coordinate_converter import (
    coordinates2segment,
    point2coordinate,
    segment2coordinates,
    segments2coordinates,
)
from src.trace_builder.model import Point, Segment


def is_dot_inside_segment(dot, segment):
    if isinstance(dot, Point):
        dot = point2coordinate(dot)
    if isinstance(segment, Segment):
        segment = segment2coordinates(segment)
    if min(segment[0][0], segment[1][0]) <= dot[0] <= max(
        segment[0][0], segment[1][0]
    ) and min(segment[0][1], segment[1][1]) <= dot[1] <= max(
        segment[0][1], segment[1][1]
    ):
        return True
    return False


def l2_distance(start, end):
    if isinstance(start, Point):
        start = point2coordinate(start)
    if isinstance(end, Point):
        end = point2coordinate(end)
    start, end = np.array(start), np.array(end)
    return np.power(((start - end) ** 2).sum(), 0.5)


def l1_distance(start, end):
    if isinstance(start, Point):
        start = point2coordinate(start)
    if isinstance(end, Point):
        end = point2coordinate(end)
    start, end = np.array(start), np.array(end)
    return np.abs(start - end).sum()


def detect_wall_with_door(segments: List[Segment]):
    segments = segments2coordinates(segments)
    segments_dict = {}
    coef2idx = {}
    for idx, segment in enumerate(segments):
        x1, y1 = segment[0]
        x2, y2 = segment[1]
        if x1 != x2:
            slope = (y2 - y1) / (x2 - x1)
            y_intercept = y1 - slope * x1
        else:
            slope = float("inf")
            y_intercept = x1
        key = (slope, y_intercept)
        if key not in segments_dict:
            segments_dict[key] = []
            coef2idx[key] = []
        segments_dict[key].append(segment)
        coef2idx[key].append(idx)
    is_walls = [False] * len(segments)
    for key, idxs in coef2idx.items():
        if len(idxs) > 1:
            for idx in idxs:
                is_walls[idx] = True
    return [
        (coordinates2segment(segment), is_wall)
        for segment, is_wall in zip(segments, is_walls)
    ]


def is_parallel_X(segment: Segment):
    return True if segment.start.y == segment.end.y else False


def is_parallel_Y(segment: Segment):
    return True if segment.start.x == segment.end.x else False


def is_wall_nighbour(wall_src, wall_dist, threshold=90):
    if (
        min(
            [
                l1_distance(wall_src.start, wall_dist.start),
                l1_distance(wall_src.start, wall_dist.end),
                l1_distance(wall_src.end, wall_dist.start),
                l1_distance(wall_src.end, wall_dist.end),
            ]
        )
        <= threshold
    ):
        return True
    return False


def is_point_near_wall(point: Point, wall: Segment, threshold: float = 90.0):
    if (
        min(
            [
                l1_distance(point, wall.start),
                l1_distance(point, wall.end),
            ]
        )
        <= threshold
    ):
        return True
    return False


def is_points_nighbour(point1, point2, threshold=90):
    if l1_distance(point1, point2) <= threshold:
        return True
    return False
