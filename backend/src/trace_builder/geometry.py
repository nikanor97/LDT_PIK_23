from model import Point, Segment
from coordinate_converter import (
    coordinate2point,
    coordinates2segment,
    coordinates2segments,
    point2coordinate,
    segment2coordinates,
    segments2coordinates,
)
import numpy as np
from typing import List


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
