# %%
from typing import List

import matplotlib.pyplot as plt

# import networkx as nx
import numpy as np

from src.trace_builder.coordinate_converter import (
    coordinate2point,
    point2coordinate,
    segment2coordinates,
)
import re
from src.trace_builder.model import Point, Segment
from src.trace_builder.geometry import (
    is_dot_inside_segment,
    l1_distance,
)

# %%


def find_rect_corners(coords, eps=1e-6):
    # Sort the coordinates by their x and values
    sorted_x = sorted(coords, key=lambda x: x[0])
    sorted_y = sorted(coords, key=lambda x: x[1], reverse=True)

    # Find the top-left and bottom-right corners of the rectangle
    top_left = (sorted_x[0][0], sorted_y[0][1])
    bottom_right = (sorted_x[-1][0], sorted_y[-1][1])

    # Find the top-right and bottom-left corners of the rectangle
    top_right, bottom_left = None, None
    for coord in coords:
        if (
            np.abs(coord[0] - top_left[0]) <= eps
            and np.abs(coord[1] - bottom_right[1]) <= eps
        ):
            bottom_left = coord
            bottom_left = (top_left[0], bottom_right[1])
        elif (
            np.abs(coord[0] - bottom_right[0]) < eps
            and np.abs(coord[1] - top_left[1]) < eps
        ):
            top_right = coord
            top_right = (bottom_right[0], top_left[1])

    # Return the corner points as a list
    return [
        np.round(top_left, 1),
        np.round(top_right, 1),
        np.round(bottom_right, 1),
        np.round(bottom_left, 1),
    ]


def wide_middle(top_left, top_right, bottom_right, bottom_left):
    mid = lambda top, bottom, coord: np.round((top[coord] + bottom[coord]) / 2, 2)
    x_left = mid(top_left, bottom_left, 0)
    y_left = mid(top_left, bottom_left, 1)
    x_right = mid(top_right, bottom_right, 0)
    y_right = mid(top_right, bottom_right, 1)
    return (x_left, y_left), (x_right, y_right)


def narrow_middle(top_left, top_right, bottom_right, bottom_left):
    mid = lambda left, right, coord: np.round((left[coord] + right[coord]) / 2, 2)
    x_upper = mid(top_left, top_right, 0)
    y_upper = mid(top_left, top_right, 1)
    x_lower = mid(bottom_left, bottom_right, 0)
    y_lower = mid(bottom_left, bottom_right, 1)
    return (x_upper, y_upper), (x_lower, y_lower)


def find_middle_points(rectangle_coordinates):
    top_left, top_right, bottom_right, bottom_left = rectangle_coordinates
    if bottom_right[0] - top_left[0] > top_left[1] - bottom_right[1]:
        return wide_middle(top_left, top_right, bottom_right, bottom_left)
    else:
        return narrow_middle(top_left, top_right, bottom_right, bottom_left)


def lin_equ(point1, point2) -> List[float]:
    k = (point2[1] - point1[1]) / (point2[0] - point1[0])
    b = point2[1] - (k * point1[0])
    return k, b


def extract_rectange_points(msp):
    hatches = msp.query("HATCH[layer=='I-WALL-3']")
    # print("HATCH", len(hatches))
    boundary_paths = []
    for hatch in hatches:
        for path in hatch.paths:
            coords = []
            for edge in path.edges:
                coords.append((edge.start[0], edge.start[1]))
            boundary_paths.append(coords)
    # print(boundary_paths)
    return boundary_paths


def entities_with_coordinates(msp):
    group = msp.groupby(dxfattrib="layer")
    sanitizing_stuff = {}
    for layer, entities in group.items():
        if layer == "P-SANR-FIXT":
            for entity in entities:
                sanitizing_stuff[entity.dxf.name] = coordinate2point(
                    tuple(entity.dxf.insert.vec2)
                )
    return sanitizing_stuff


def extract_riser_coordinates(doc):
    center = None
    for entity in doc.entities:
        if entity.dxf.layer == "A-DETL" and entity.dxf.dxftype == "CIRCLE":
            center = (
                np.round(entity.dxf.center.x, 2),
                np.round(entity.dxf.center.y, 2),
            )
            center = coordinate2point(center)
    return center


def filter_wall_by_distance(segment: Segment, dist_threshold: float):
    start, end = np.array(segment2coordinates(segment))
    return True if l1_distance(start, end) >= dist_threshold else False


def projection(point, line):
    if isinstance(point, Point):
        point = point2coordinate(point)
    if isinstance(line, Segment):
        line = segment2coordinates(line)
    (x1, y1), (x2, y2) = line

    # Check if the line is parallel to the x-axis
    if y1 == y2:
        return Point(point[0], y1)

    # Check if the line is parallel to the y-axis
    if x1 == x2:
        return Point(x1, point[1])

    # Calculate the slope and y-intercept of the line
    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1

    # Calculate the x-coordinate of the projection point
    x = (m * point[1] + point[0] / m + b) / (1 / m + m)

    # Calculate the y-coordinate of the projection point
    y = m * x + b

    # Return the projection point as a tuple
    return Point(x, y)


def projection_point(point: Point, segment: Segment) -> Point:
    # Check if the line is parallel to the x-axis
    if segment.start.y == segment.end.y:
        return Point(point.x, segment.start.y)

    # Check if the line is parallel to the y-axis
    if segment.start.x == segment.end.x:
        return Point(segment.start.x, point.y)

    # Calculate the slope and y-intercept of the line
    m = (segment.end.y - segment.start.y) / (segment.end.x - segment.start.x)
    b = segment.start.y - m * segment.start.x

    # Calculate the x-coordinate of the projection point
    x = (m * point.y + point.x / m + b) / (1 / m + m)

    # Calculate the y-coordinate of the projection point
    y = m * x + b

    # Return the projection point as a tuple
    return Point(x, y)


def get_stuff_projcetions(stuffs, segments, verbose=False):
    stuff_projection = {}
    for stuff, coordinates in stuffs.items():
        min_dist, best_segmet, best_projectioned = float("inf"), None, None
        if verbose:
            plt.scatter(coordinates.x, coordinates.y, marker="*", linewidths=3)
        for segment, is_has_door in segments:
            projectioned = projection(coordinates, segment)
            # seg = Segment(Point(segment[0][0], segment[0][1]), Point(segment[1][0], segment[1][1]))
            # projectioned_point = projection(Point(coordinates[0], coordinates[1]), seg)
            if verbose:
                x = segment.start.x, segment.end.x
                y = segment.start.y, segment.end.y
                plt.plot(x, y)
                plt.scatter(projectioned.x, projectioned.y)
            l1_dist = l1_distance(coordinates, projectioned)
            if not is_dot_inside_segment(projectioned, segment):
                l1_dist += min(
                    l1_distance(projectioned, segment.start),
                    l1_distance(projectioned, segment.end),
                )
            if (l1_dist < min_dist or not best_segmet) and not is_has_door:
                min_dist = l1_dist
                best_segmet = segment
                best_projectioned = projectioned
        stuff_projection[stuff] = {
            "coordinates": coordinates,
            "segment": best_segmet,
            "projection": best_projectioned,
            "l1_projection": min_dist,
        }
        if verbose:
            x = coordinates.x, best_projectioned.x
            y = coordinates.y, best_projectioned.y
            plt.plot(x, y)
            plt.show()
    return stuff_projection


def build_riser_projections(riser: Point, segments: List[Segment]):
    projections = []
    for segment in segments:
        projectioned = projection(riser, segment)
        l1_dist = l1_distance(riser, projectioned)
        if not is_dot_inside_segment(projectioned, segment):
            l1_dist += min(
                l1_distance(projectioned, segment.start),
                l1_distance(projectioned, segment.end),
            )
            # print(projectioned, "not in ", segment, "L1", l1_dist)
        projections.append((segment, projectioned, l1_dist))
    return projections


def find_optimal_riser_projection(riser_projections, stuff_projections):
    best_dist, best_project = float("inf"), None
    for idx_projection, riser_projection in enumerate(riser_projections):
        cum_sum = 0
        segment, projected_point, l1_dist = riser_projection
        for stuff, info in stuff_projections.items():
            cum_sum += l1_distance(projected_point, info["projection"])
        if cum_sum < best_dist:
            best_project = riser_projection
            best_dist = cum_sum
            best_idx_projection = idx_projection
    return best_idx_projection


def plot_projcetions(
    riser_coordinates, riser_projections, stuff_projections, optimal_segment
):
    for idx, riser_projection in enumerate(riser_projections):
        segment, projectioned, l1_dist = riser_projection
        x = segment.start.x, segment.end.x
        y = segment.start.y, segment.end.y
        linewidth = 1 if idx != optimal_segment else 3
        plt.plot(x, y, label=idx, linewidth=linewidth)
        if idx == optimal_segment:
            plt.plot(
                (riser_coordinates.x, projectioned.x),
                (riser_coordinates.y, projectioned.y),
                linewidth=3,
            )

    for stuff, info in stuff_projections.items():
        stuff_coordinates = info["coordinates"]
        stuff_projection = info["projection"]
        plt.scatter(stuff_coordinates.x, stuff_coordinates.y, marker="*")
        plt.scatter(stuff_projection.x, stuff_projection.y)
        plt.plot(
            (stuff_projection.x, stuff_coordinates.x),
            (stuff_projection.y, stuff_coordinates.y),
        )
    plt.legend()
    plt.grid()
    plt.show()


def distance_from_riser_to_stuff(riser_projection, stuff_projections):
    for stuff, info in stuff_projections.items():
        stuff_projections[stuff]["riser_l1_distance"] = l1_distance(
            stuff_projections[stuff]["projection"], riser_projection
        )
    return stuff_projections


def calculate_max_riser_height(stuffs):
    best_min_dist = float("inf")
    for stuff, info in stuffs.items():
        min_dist = max(info["height"] - info["riser_l1_distance"] * 0.02, 50)
        best_min_dist = min(best_min_dist, min_dist)
    return best_min_dist


def clear_sutff_duplicate(stuffs):
    keys_to_delete = []
    first = True
    for key in stuffs.keys():
        if re.search(".*[Вв]анн.*", key):
            if not first:
                keys_to_delete.append(key)
            else:
                first = False

    for key in keys_to_delete:
        stuffs.pop(key, None)
    return stuffs


# %% Extract rectange coordinates

# doc = ezdxf.readfile(
#     "/Users/valentin/Projects/pik/experiments/data/cabin_examples/СТМ8-1П-Б-2.dxf"
# )
# modelspace = doc.modelspace()
# msp = modelspace


# riser_coordinates = extract_riser_coordinates(doc)
# print(riser_coordinates)
# coordinates = extract_rectange_points(msp)
# # pprint(coordinates)
# rectangle_coordinates = [
#     find_rect_corners(coordinate, 0.5) for coordinate in coordinates
# ]
# mid_points = [find_middle_points(coordinate) for coordinate in rectangle_coordinates]
# mid_points_ = coordinates2segments(mid_points)


# # print(mid_points)
# # line_coeffs = [lin_equ(*points) for points in mid_points]

# stuffs = entities_with_coordinates(msp)
# for segment in mid_points_:
#     # x = point[0][0], point[1][0]
#     # y = point[0][1], point[1][1]
#     x = segment.start.x, segment.end.x
#     y = segment.start.y, segment.end.y
#     plt.plot(x, y)
# for name, point in stuffs.items():
#     plt.scatter(point.x, point.y)
# plt.show()

# mid_points_merged = merge_segments(mid_points_, 100)
# mid_points_merged = merge_segments(mid_points_merged, 100)
# mid_point_filtered = [
#     segment for segment in mid_points_merged if filter_wall_by_distance(segment, 100)
# ]
# pprint(mid_point_filtered)


# for segment in mid_point_filtered:
#     x = segment.start.x, segment.end.x
#     y = segment.start.y, segment.end.y
#     plt.plot(x, y)
# for name, point in stuffs.items():
#     plt.scatter(point.x, point.y)
# plt.scatter(riser_coordinates.x, riser_coordinates.y)
# plt.legend()
# plt.grid()
# plt.show()

# segments_with_wall_flag = detect_wall_with_door(mid_point_filtered)

# # point = stuffs["АИ_2D_Ванна 1685х700 - 2D_Ванна 1700х700-16267569-Битца 8_ТИПИЗАЦИЯ"]
# # line = mid_point_filtered[6]
# # for line in mid_point_filtered:
# #     print("Point", point, "Line", line, "Projection", projection(point, line))

# stuff_projections = get_stuff_projcetions(stuffs, segments_with_wall_flag, True)

# riser_projection_distances = build_riser_projections(riser_coordinates, mid_point_filtered)

# optimal_segment = find_optimal_riser_projection(
#     riser_projection_distances, stuff_projections
# )
# riser_projection = projection(riser_coordinates, mid_point_filtered[optimal_segment])
# plot_projcetions(
#     riser_coordinates, riser_projection_distances, stuff_projections, optimal_segment
# )

# distance_from_riser_to_stuff(riser_projection, stuff_projections)

# hieghts = {
#     "SND_2D_Раковина1 - 550х400-16253994-Битца 8_ТИПИЗАЦИЯ": 100,
#     "SEQ_2D_Стиральная машина - 600x600-V57-Битца 8_ТИПИЗАЦИЯ": 200,
#     "АИ_2D_Ванна 1685х700 - 2D_Ванна 1700х700-16267569-Битца 8_ТИПИЗАЦИЯ": 300,
#     "АИ_2D_Кран настенный для ванны с душем1 - 2D_Кран настенный для ванны с душем 2-16267571-Битца 8_ТИПИЗАЦИЯ": 300,
#     "SND_2D_Эскиз_Мойка_Кухня - SND_2D_Эскиз_Мойка_Кухня-16115635-Битца 8_ТИПИЗАЦИЯ": 150,
#     "Унитаз_3D_С бачком_Рен - 2D_Унитаз_Бачок-V58-Битца 8_ТИПИЗАЦИЯ": 100,
# }

# for key in stuff_projections.keys():
#     stuff_projections[key]["height"] = hieghts[key]


# max_riser_height = calculate_max_riser_height(stuff_projections)
# # %%
# clear_sutff_duplicate(stuff_projections)

# # %%
# save_data(
#     stuffs=stuff_projections,
#     walls=mid_point_filtered,
#     max_riser_height=max_riser_height,
#     optimal_segment=optimal_segment,
#     riser_coordinates=riser_coordinates,
#     riser_projection=riser_projection
# )

# # %%
# stuff_projections, mid_point_filtered, max_riser_height, optimal_segment = load_data(
#     "geometry.json"
# )
