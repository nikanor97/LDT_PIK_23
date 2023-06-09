# %%
import re
from random import randint
from typing import List

import ezdxf
import matplotlib.pyplot as plt

# import networkx as nx
import numpy as np
from src.trace_builder.coordinate_converter import (
    coordinate2point,
    coordinates2segments,
    point2coordinate,
    segment2coordinates,
)
from src.trace_builder.geometry import (
    is_dot_inside_segment,
    is_parallel_X,
    is_parallel_Y,
    is_point_near_wall,
    is_points_nighbour,
    is_wall_nighbour,
    l1_distance,
    l2_distance,
)
from src.trace_builder.merge_segments import merge_segments
from src.trace_builder.model import DXFStuff, Point, Segment
from src.trace_builder.models import Stuff, Wall
from src.trace_builder.path import (
    build_path_from_riser_wall_to_sutff_wall,
    detect_walls_with_stuff,
    get_neighbour_wall,
)
from src.trace_builder.utils import dict2stuff

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


def stuff_with_coordinates(msp):
    group = msp.groupby(dxfattrib="layer")
    stuffs = []
    id = 0
    first_occour_bath = True
    for layer, entities in group.items():
        if layer == "P-SANR-FIXT":
            for entity in entities:
                entity_name = entity.dxf.name
                coordinates = coordinate2point(tuple(entity.dxf.insert.vec2))
                if re.search(".*[Вв]анн.*", entity_name):
                    if not first_occour_bath:
                        continue
                    first_occour_bath = False
                stuffs.append(DXFStuff(id, entity_name, coordinates))
                id += 1
    return stuffs


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
        # for segment, is_has_door in segments:
        for segment in segments:
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
            if l1_dist < min_dist or not best_segmet:
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
            cum_sum += np.log(l2_distance(projected_point, info["projection"]))
        cum_sum += l1_dist**2
        # print(idx_projection, cum_sum, l1_dist)
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
            plt.scatter(
                riser_coordinates.x,
                riser_coordinates.y,
                linewidth=3,
                marker="X",
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


def get_top3_segmets(segments, topk=3):
    for segment in segments:
        segment.length = l1_distance(segment.start, segment.end)
    return sorted(segments, key=lambda x: x.length, reverse=True)[:topk]


def update_wall_y(wall_for_update, reference_wall_bad, reference_wall_good):
    if is_point_near_wall(wall_for_update.end, reference_wall_good):
        delt = wall_for_update.end.y - reference_wall_good.start.y
        wall_for_update.start.y = reference_wall_bad.start.y - delt
    else:
        delt = wall_for_update.start.y - reference_wall_good.start.y
        wall_for_update.end.y = reference_wall_bad.start.y
    return wall_for_update


def update_wall_x(wall_for_update, reference_wall_bad, reference_wall_good):
    if is_point_near_wall(wall_for_update.end, reference_wall_good):
        delt = wall_for_update.end.x - reference_wall_good.start.x
        wall_for_update.start.x = reference_wall_bad.start.y - delt
    else:
        delt = wall_for_update.start.x - reference_wall_good.start.x
        wall_for_update.end.x = reference_wall_bad.start.y - delt
    return wall_for_update


def check_wall_coordinates(walls):
    parallel_x_cnt, parallel_y_cnt = 0, 0
    parallel_x_walls = []
    parallel_y_walls = []
    out_walls = []
    for wall in walls:
        if is_parallel_X(wall):
            parallel_x_cnt += 1
            parallel_x_walls.append(wall)
        if is_parallel_Y(wall):
            parallel_y_cnt += 1
            parallel_y_walls.append(wall)
    if parallel_x_cnt == 2 and parallel_y_cnt == 1:
        if is_wall_nighbour(
            parallel_x_walls[0], parallel_y_walls[0]
        ) and not is_wall_nighbour(parallel_x_walls[1], parallel_y_walls[0]):
            parallel_y_walls[0] = update_wall_y(
                parallel_y_walls[0], parallel_x_walls[1], parallel_x_walls[0]
            )
        elif not is_wall_nighbour(
            parallel_x_walls[0], parallel_y_walls[0]
        ) and is_wall_nighbour(parallel_x_walls[1], parallel_y_walls[0]):
            parallel_y_walls[0] = update_wall_y(
                parallel_y_walls[0], parallel_x_walls[0], parallel_x_walls[1]
            )
        out_walls = parallel_x_walls + parallel_y_walls
    elif parallel_x_cnt == 1 and parallel_y_cnt == 2:
        if is_wall_nighbour(
            parallel_x_walls[0], parallel_y_walls[0]
        ) and not is_wall_nighbour(parallel_x_walls[0], parallel_y_walls[1]):
            parallel_x_walls[0] = update_wall_x(
                parallel_x_walls[0], parallel_y_walls[1], parallel_y_walls[0]
            )
        elif is_wall_nighbour(
            parallel_x_walls[0], parallel_y_walls[1]
        ) and not is_wall_nighbour(parallel_x_walls[0], parallel_y_walls[0]):
            parallel_x_walls[0] = update_wall_x(
                parallel_x_walls[0], parallel_y_walls[0], parallel_y_walls[1]
            )
        out_walls = parallel_x_walls + parallel_y_walls
    else:
        out_walls = walls
    return out_walls


def get_toilet_stuff(stuffs: List[Stuff]) -> Stuff:
    for stuff in stuffs:
        if stuff.is_toilet:
            return stuff


def detect_walls_after_toilet(
    walls: List[Wall], riser_projeciton: Point, toilet_projection: Point
):
    for wall in walls:
        if wall.has_toilet:
            wall.after_toilet = True
    for wall in walls:
        if wall.has_toilet:
            continue
        if is_parallel_X(wall):
            if wall.coordinates.start.y < toilet_projection.projection.y:
                if toilet_projection.projection.y < riser_projeciton.y:
                    wall.after_toilet = True
                elif toilet_projection.projection.y == riser_projeciton.y:
                    if (
                        wall.path2wall_with_riser[0].coordinates.start.x
                        < toilet_projection.projection.x
                        < riser_projeciton.x
                    ):
                        wall.after_toilet = True
                    if (
                        wall.path2wall_with_riser[0].coordinates.start.x
                        > toilet_projection.projection.x
                        > riser_projeciton.x
                    ):
                        wall.after_toilet = True
            elif wall.coordinates.start.y > toilet_projection.projection.y:
                if toilet_projection.projection.y > riser_projeciton.y:
                    wall.after_toilet = True
                elif toilet_projection.projection.y == riser_projeciton.y:
                    if (
                        wall.path2wall_with_riser[0].coordinates.start.x
                        < toilet_projection.projection.x
                        < riser_projeciton.x
                    ):
                        wall.after_toilet = True
                    if (
                        wall.path2wall_with_riser[0].coordinates.start.x
                        > toilet_projection.projection.x
                        > riser_projeciton.x
                    ):
                        wall.after_toilet = True
            else:
                if toilet_projection.projection.y != riser_projeciton.y:
                    wall.after_toilet = True
        else:
            if (
                wall.coordinates.start.y < toilet_projection.projection.y
                and toilet_projection.projection.y < riser_projeciton.y
            ):
                wall.after_toilet = True
            if wall.coordinates.start.x > toilet_projection.projection.x:
                if toilet_projection.projection.x > riser_projeciton.x:
                    wall.after_toilet = True
                elif toilet_projection.projection.x == riser_projeciton.x:
                    if (
                        wall.path2wall_with_riser[0].coordinates.start.y
                        > toilet_projection.projection.y
                        > riser_projeciton.y
                    ):
                        wall.after_toilet = True
                    if (
                        wall.path2wall_with_riser[0].coordinates.start.y
                        < toilet_projection.projection.y
                        < riser_projeciton.y
                    ):
                        wall.after_toilet = True
            elif wall.coordinates.start.x < toilet_projection.projection.x:
                if toilet_projection.projection.x < riser_projeciton.x:
                    wall.after_toilet = True
                elif toilet_projection.projection.x == riser_projeciton.x:
                    if (
                        wall.path2wall_with_riser[0].coordinates.start.y
                        > toilet_projection.projection.y
                        > riser_projeciton.y
                    ):
                        wall.after_toilet = True
                    if (
                        wall.path2wall_with_riser[0].coordinates.start.y
                        < toilet_projection.projection.y
                        < riser_projeciton.y
                    ):
                        wall.after_toilet = True
            else:
                if toilet_projection.projection.x != riser_projeciton.x:
                    wall.after_toilet = True


def get_length_from_riser_projection(
    wall_src: Wall, will_with_riser: Wall, riser_projection: Point
):
    wall_riser_point = get_neighbour_wall(will_with_riser, wall_src)
    return l1_distance(wall_riser_point, riser_projection)


def calculate_wall_slope_shift(walls: List[Wall], riser_projection: Point):
    for wall in walls:
        if not wall.with_riser:
            cumm_lenght = 0
            walls_paths = wall.path2wall_with_riser
            for wall_path in walls_paths:
                if wall_path.with_riser:
                    src_wall = (
                        wall
                        if len(wall.path2wall_with_riser) == 1
                        else wall.path2wall_with_riser[-2]
                    )
                    cumm_lenght += get_length_from_riser_projection(
                        src_wall, wall_path, riser_projection
                    )
                else:
                    cumm_lenght += wall_path.length
            wall.cumm_slope_shift = cumm_lenght * 0.02


def process_file_geometry(dxf_path, heighs):
    doc = ezdxf.readfile(dxf_path)
    modelspace = doc.modelspace()
    msp = modelspace

    # from src.trace_builder.utils import convert_dxf2img
    # convert_dxf2img(doc, settings.MEDIA_DIR / "builder_outputs" / "test.png")
    riser_coordinates = extract_riser_coordinates(doc)
    coordinates = extract_rectange_points(msp)
    rectangle_coordinates = [
        find_rect_corners(coordinate, 0.5) for coordinate in coordinates
    ]
    mid_points = [
        find_middle_points(coordinate) for coordinate in rectangle_coordinates
    ]
    mid_points_ = coordinates2segments(mid_points)

    stuffs = entities_with_coordinates(msp)
    # stuffs = stuff_with_coordinates(msp)

    mid_points_merged = merge_segments(mid_points_, 100)
    mid_points_merged = merge_segments(mid_points_merged, 100)
    mid_point_filtered = [
        segment
        for segment in mid_points_merged
        if filter_wall_by_distance(segment, 100)
    ]
    mid_point_filtered = get_top3_segmets(mid_point_filtered)
    mid_point_filtered = check_wall_coordinates(mid_point_filtered)
    # segments_with_wall_flag = detect_wall_with_door(mid_point_filtered)

    stuff_projections = get_stuff_projcetions(stuffs, mid_point_filtered)

    riser_projection_distances = build_riser_projections(
        riser_coordinates, mid_point_filtered
    )

    optimal_segment = find_optimal_riser_projection(
        riser_projection_distances, stuff_projections
    )
    riser_projection = projection(
        riser_coordinates, mid_point_filtered[optimal_segment]
    )
    # if os.getenv("LOCAL_ALGO"):
    #     plot_projcetions(riser_coordinates, riser_projection_distances, stuff_projections, optimal_segment)

    distance_from_riser_to_stuff(riser_projection, stuff_projections)

    for key in stuff_projections.keys():
        stuff_projections[key]["height"] = heighs.get(key, randint(150, 350))

    max_riser_height = calculate_max_riser_height(stuff_projections)

    clear_sutff_duplicate(stuff_projections)
    stuffs = stuff_projections
    walls_segments = mid_point_filtered
    riser_projections = riser_projection
    stuffs_objects = dict2stuff(stuffs)

    walls = detect_walls_with_stuff(stuffs_objects, walls_segments, riser_projections)
    walls = sorted(walls, key=lambda x: x.length, reverse=True)[:3]
    walls = build_path_from_riser_wall_to_sutff_wall(walls)

    toilet = get_toilet_stuff(stuffs_objects)
    detect_walls_after_toilet(walls, riser_projections, toilet)
    calculate_wall_slope_shift(walls, riser_projections)
    return walls, riser_projections, riser_coordinates, max_riser_height
