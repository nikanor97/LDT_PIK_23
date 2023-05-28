# %%
from typing import List, Tuple

from coordinate_converter import (
    coordinate2point,
    coordinates2segment,
    coordinates2segments,
    point2coordinate,
    segments2coordinates,
)
from model import Point, Segment


def merge_segments(segments: List[Segment], eps: float):
    segments = segments2coordinates(segments)
    #  -> List[[Tuple[float, float], Tuple[float, float]]]:
    # Create a dictionary to group segments by their slope and y-intercept
    segments_dict = {}
    for segment in segments:
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
        segments_dict[key].append(segment)

    # Merge segments on the same line and close enough to each other
    merged_segments = []
    for key, segments_list in segments_dict.items():
        if key[0] == float("inf"):
            segments_list = sorted(segments_list, key=lambda x: x[1])
        segments_list.sort()
        current_segment = segments_list[0]
        x1, y1 = current_segment[0]
        x2, y2 = current_segment[1]
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        for i in range(1, len(segments_list)):
            next_segment = segments_list[i]
            x1_next, y1_next = next_segment[0]
            x2_next, y2_next = next_segment[1]
            if key[0] == float("inf"):
                if abs(y1_next - y2) <= eps and min(x1_next, x2_next) <= max_x + eps:
                    max_x = max(x2_next, max_x)
                    max_y = max(y1_next, max_y, y2_next)
                else:
                    merged_segments.append(((min_x, min_y), (max_x, max_y)))
                    x1, y1 = x1_next, y1_next
                    x2, y2 = x2_next, y2_next
                    min_x, max_x = min(x1, x2), max(x1, x2)
                    min_y, max_y = min(y1, y2), max(y1, y2)
            else:
                if (
                    abs(key[0] * x1_next + key[1] - y1_next) <= eps
                    and min(x1_next, x2_next) <= max_x + eps
                ):
                    max_x = max(x2_next, max_x)
                    max_y = max(y1_next, max_y, y2_next)
                else:
                    merged_segments.append(((min_x, min_y), (max_x, max_y)))
                    x1, y1 = x1_next, y1_next
                    x2, y2 = x2_next, y2_next
                    min_x, max_x = min(x1, x2), max(x1, x2)
                    min_y, max_y = min(y1, y2), max(y1, y2)
        merged_segments.append(((min_x, min_y), (max_x, max_y)))
    return coordinates2segments(merged_segments)
