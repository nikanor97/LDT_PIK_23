# %%
import math
import os
import re
from typing import List, Tuple

import numpy as np
import vtkplotlib as vpl
from src.trace_builder.constants import FITTINGS, GLOBAL_INIT_MIN
from src.trace_builder.geometry import (is_dot_inside_segment, is_parallel_X,
                                        is_parallel_Y, is_wall_nighbour,
                                        l1_distance)
from src.trace_builder.graph_models import Node, PipeGraph
from src.trace_builder.manipulate_3d import (build_knee_fitting,
                                             build_otvod_to_knee_pipe,
                                             build_pipe_mesh, build_riser,
                                             build_riser_otvod,
                                             build_riser_to_otvod_pipe,
                                             build_stuff_mesh_45,
                                             build_toilet_mesh,
                                             build_knee_fitting_45,
                                             build_pipe_arrows,
                                             draw_bath_arrows)
from src.trace_builder.mesh_3d.stuff_30_15 import build_stuff_mesh_30_15
from src.trace_builder.mesh_3d.stuff_87 import build_stuff_mesh_87
from src.trace_builder.meterial_graph import build_material_graph
from src.trace_builder.model import Point, Segment
from src.trace_builder.models import Pipe, Wall
from stl import mesh


def is_toilet(stuff) -> bool:
    return True if bool(re.search(".*[Уу]нитаз.*", stuff)) else False


def detect_walls_with_stuff(
    stuffs, walls, riser_projections
) -> List[Tuple[Wall, bool, bool]]:
    walls_with_stuff = []

    for wall in walls:
        flag_wall_with_stuff, flag_is_toilet = False, False
        stuff_in_wall = []
        for stuff in stuffs:
            is_stuff_with_wall = is_dot_inside_segment(stuff.projection, wall)
            if is_stuff_with_wall:
                flag_wall_with_stuff = True
                if is_toilet(stuff.name):
                    flag_is_toilet = True
                stuff_in_wall.append(stuff)
        is_stuff_with_riser = is_dot_inside_segment(riser_projections, wall)
        wall_info = Wall(
            wall=wall,
            has_stuff=flag_wall_with_stuff,
            has_toilet=flag_is_toilet,
            stuff_point=stuff_in_wall,
            with_riser=is_stuff_with_riser,
        )
        walls_with_stuff.append(wall_info)
    return walls_with_stuff


def get_neighbour_wall(wall_src, wall_dist, threshold=90):
    if (
        min(
            [
                l1_distance(wall_src.start, wall_dist.start),
                l1_distance(wall_src.start, wall_dist.end),
            ]
        )
        <= threshold
    ):
        return wall_src.start
    elif (
        min(
            [
                l1_distance(wall_src.end, wall_dist.start),
                l1_distance(wall_src.end, wall_dist.end),
            ]
        )
        <= threshold
    ):
        return wall_src.end
    else:
        return None


def build_path_from_riser_wall_to_sutff_wall(walls: List[Wall]):
    walls_new = []
    for idx, wall in enumerate(walls):
        if wall.with_riser:
            walls_new.append(wall)
            continue
        for idx2, wall2 in enumerate(walls):
            if wall == wall2:
                continue
            if is_wall_nighbour(wall, wall2):
                if wall2.with_riser:
                    wall.path2wall_with_riser = [wall2]
                    wall.start_pipe_point = get_neighbour_wall(wall, wall2)
                else:
                    riser_idx = set([0, 1, 2])
                    riser_idx.remove(idx)
                    riser_idx.remove(idx2)
                    riser_idx = list(riser_idx)[0]
                    path = [wall2, walls[riser_idx]]
                    wall.path2wall_with_riser = path
                if not wall.start_pipe_point:
                    wall.start_pipe_point = get_neighbour_wall(wall, wall2)
                walls_new.append(wall)
    return walls_new


def estimate_min_height(wall, riser_projections):
    if not wall.path2wall_with_riser:
        min_height = 0
    elif len(wall.path2wall_with_riser) == 1:
        min_height = l1_distance(wall.start_pipe_point, riser_projections) * 0.02
    else:
        penultimate_point_on_riser_projection = min(
            l1_distance(wall.path2wall_with_riser[-2].start, riser_projections),
            l1_distance(wall.path2wall_with_riser[-2].end, riser_projections),
        )
        min_height = (
            sum([wall_path.length for wall_path in wall.path2wall_with_riser[:-1]])
            + penultimate_point_on_riser_projection
        ) * 0.02
    return min_height + GLOBAL_INIT_MIN


def get_nearest_wall_to_point(point, wall_src, walls):
    best_dist = float("inf")
    best_wall = None
    for idx, wall in enumerate(walls):
        if wall_src == wall:
            continue
        dist = min(l1_distance(point, wall.start), l1_distance(point, wall.end))
        if not best_wall or best_dist > dist:
            best_wall = idx
            best_dist = dist
    return walls[best_wall], best_dist

def _define_start(wall):
    is_last_stuff_is_edged = True
    if is_parallel_Y(wall):
        if wall.start_pipe_point.y > wall.stuff_point[0].projection.y:
            start = Point(
                wall.start_pipe_point.x,
                min([point.projection.y for point in wall.stuff_point]),
            )
            wall.stuff_point = sorted(wall.stuff_point, key=lambda x: x.projection.y)
            is_last_stuff_is_edged = False
        else:
            start = Point(
                wall.start_pipe_point.x,
                max([point.projection.y for point in wall.stuff_point]),
            )
            wall.stuff_point = sorted(
                wall.stuff_point, key=lambda x: x.projection.y, reverse=True
            )
    else:
        if wall.start_pipe_point.x > wall.stuff_point[0].projection.x:
            start = Point(
                min([point.projection.x for point in wall.stuff_point]),
                wall.start_pipe_point.y,
            )
            wall.stuff_point = sorted(wall.stuff_point, key=lambda x: x.projection.x)
            is_last_stuff_is_edged = False
        else:
            start = Point(
                max([point.projection.x for point in wall.stuff_point]),
                wall.start_pipe_point.y,
            )
            wall.stuff_point = sorted(
                wall.stuff_point, key=lambda x: x.projection.x, reverse=True
            )
    return start, is_last_stuff_is_edged


def count_pipes_for_wall_with_stuff(wall, walls, riser_projections):
    start, end = None, wall.start_pipe_point
    start, is_last_stuff_is_edged = _define_start(wall)
    if len(wall.stuff_point) == 1:
        # TODO FIX Pipe in wrong direction if not neigbouri with riser
        start_end_pipes = [
            Pipe(
                coordinates=Segment(start, end),
                is_toilet=wall.has_toilet,
                with_riser=wall.with_riser,
                is_end=True,
                is_start=True,
                stuff=wall.stuff_point[0],
                is_wall_start=True
            )
        ]
    else:
        start_end_pipes = []
        for idx_stuff, stuff in enumerate(wall.stuff_point[:-1]):
            start_end_pipes.append(
                Pipe(
                    coordinates=Segment(
                        start, wall.stuff_point[idx_stuff + 1].projection
                    ),
                    is_toilet=stuff.is_toilet,
                    with_riser=wall.with_riser,
                    stuff=stuff,
                )
            )
            start = wall.stuff_point[idx_stuff + 1].projection
        start_end_pipes.append(
            Pipe(
                coordinates=Segment(start, end),
                is_toilet=wall.stuff_point[-1].is_toilet,
                with_riser=wall.with_riser,
                stuff=wall.stuff_point[-1],
            )
        )
        if is_last_stuff_is_edged:
            start_end_pipes[-1].is_end = True
            start_end_pipes[0].is_start = True
            start_end_pipes[0].is_wall_start = True
        else:
            start_end_pipes[0].is_end = True
            start_end_pipes[-1].is_start = True
            start_end_pipes[-1].is_wall_start = True
    min_height = estimate_min_height(wall, riser_projections)
    point = wall.start if wall.start != wall.start_pipe_point else wall.end
    end_wall, end_wall_dist = get_nearest_wall_to_point(point, wall, walls)
    if end_wall_dist < 500 and (
        end_wall.has_stuff or if_wall_in_path_for_riser(end_wall, walls)
    ):
        if is_last_stuff_is_edged:
            start_end_pipes.append(
                Pipe(
                    coordinates=Segment(point, start_end_pipes[-1].coordinates.start),
                    is_toilet=False,
                    with_riser=False,
                    stuff=None,
                    is_end=True,
                    is_wall_end=True,
                )
            )
            start_end_pipes[-2].is_end = False
        else:
            start_end_pipes = [
                Pipe(
                    coordinates=Segment(point, start_end_pipes[-1].coordinates.start),
                    is_toilet=False,
                    with_riser=False,
                    stuff=None,
                    is_end=True,
                    is_wall_end=True,
                )
            ] + start_end_pipes
            start_end_pipes[1].is_end = False
    return start_end_pipes, min_height


def if_wall_in_path_for_riser(wall, walls):
    is_wall_neigbour_for_riser = False
    is_wall_neighbour_for_pipe_with_stuff = False
    for wall_ in walls:
        if wall == wall_:
            continue
        if is_wall_nighbour(wall, wall_):
            if wall_.with_riser:
                is_wall_neigbour_for_riser = True
            elif wall_.has_stuff:
                is_wall_neighbour_for_pipe_with_stuff = True
    if is_wall_neigbour_for_riser & is_wall_neighbour_for_pipe_with_stuff:
        return True
    return False


def wall_with_riser(wall_riser, riser_projections):
    start_end_pipes = []
    end = wall_riser.start
    start = riser_projections
    start_end_pipes.append(Segment(start, end))
    end = wall_riser.end
    start_end_pipes.append(Segment(start, end))
    return start_end_pipes

def is_riser_otvod_both_side(walls: List[Wall], riser_projections: Point) -> bool:
    left, right, down, up = False, False, False, False
    for wall in walls:
        if wall.with_riser:
            for stuff in wall.stuff_point:
                if is_parallel_X(wall.coordinates):
                    if stuff.projection.x < riser_projections.x:
                        left = True
                    else:
                        right = True
                if is_parallel_Y(wall.coordinates):
                    if stuff.projection.y > riser_projections.y:
                        up = True
                    else:
                        down = True
        else:
            if is_parallel_X(wall.coordinates):
                if len(wall.path2wall_with_riser) == 1:
                    if wall.start_pipe_point.y < riser_projections.y:
                        down = True
                    else:
                        up = True
                else:
                    if wall.start_pipe_point.x <= riser_projections.x:
                        left = True
                    else:
                        right = True
            else:
                if len(wall.path2wall_with_riser) == 1:
                    if wall.start_pipe_point.x < riser_projections.x:
                        left = True
                    else:
                        right = True
                else:
                    if wall.start_pipe_point.y <= riser_projections.y:
                        down = True
                    else:
                        up = True
    return (left and right) or (up and down)


def process_artifacts(mesh_data, material_graph, scrennshot_name, walls):
    all_figures = mesh.Mesh(np.concatenate(mesh_data))
    grap_df = build_material_graph(material_graph)
    figure = vpl.gcf()
    plotted_mesh = vpl.mesh_plot(all_figures)
    draw_bath_arrows(walls, 50)
    vpl.view(camera_direction=(0.1, 0.6, -0.8))
    vpl.save_fig(scrennshot_name, pixels=(1920, 1080))
    if os.getenv("LOCAL_ALGO"):
        vpl.show()
    figure -= plotted_mesh
    figure.close()
    return all_figures, grap_df

def build_mesh_path(walls, riser_projections, riser_coordinates, scrennshot_name, scenario="87"):
    material_graph = PipeGraph()
    mesh_data = []
    # riser_coordinates.y -= 200
    bi = 0
    riser_coordinates_test = Point(riser_coordinates.x + bi, riser_coordinates.y + bi)
    riser_projections_test = Point(riser_projections.x + bi, riser_projections.y + bi)
    # riser_coordinates_test.y -= 1000
    # riser_coordinates_test.x -= 900
    # riser_projections_test.x -= 900
    # riser_projections_test.y -= 400
    # riser_projections_test.y  = riser_coordinates_test.y
    riser_obj, node = build_riser(riser_coordinates_test, riser_projections_test, walls)
    mesh_data.append(riser_obj.data.copy())
    material_graph.add_node(node)
    # print("Both", is_riser_otvod_both_side(walls, riser_projections))
    riser_obj_p, node = build_riser_to_otvod_pipe(
        riser_coordinates_test, riser_projections_test
    )
    if riser_obj_p:
        mesh_data.append(riser_obj_p.data.copy())
        material_graph.add_node(node)
    is_both_side = is_riser_otvod_both_side(walls, riser_projections)
    pipe_turn, node = build_riser_otvod(
        riser_coordinates_test, riser_projections_test, walls, is_both_side
    )
    mesh_data.append(pipe_turn.data.copy())
    material_graph.add_node(node)
    for wall in walls:
        obj = FITTINGS["d50"]
        if not wall.with_riser and wall.has_stuff:
            # TODO move end for enable right turn
            pipes, start_height = count_pipes_for_wall_with_stuff(
                wall, walls, riser_projections
            )
            for idx, pipe in enumerate(pipes):
                if os.getenv("LOCAL_ALGO"):
                    build_pipe_arrows(pipe)
                obj = FITTINGS["d110"] if pipe.is_toilet else FITTINGS["d50"]
                mesh_obj, node = build_pipe_mesh(
                    obj, pipe, scenario
                )
                mesh_data.append(mesh_obj.data.copy())
                material_graph.add_node(node)
                if pipe.is_toilet:
                    toilet_objets = build_toilet_mesh(pipe, material_graph)
                    mesh_data.extend([objects.data.copy() for objects in toilet_objets])
                else:
                    if pipe.stuff:
                        if scenario == "87":
                            stuff_object = build_stuff_mesh_87(pipe, material_graph)
                        elif scenario == "45":
                            stuff_object = build_stuff_mesh_45(pipe, material_graph)
                        elif scenario == "30_15":
                            stuff_object = build_stuff_mesh_30_15(pipe, material_graph)
                        mesh_data.extend(
                            [objects.data.copy() for objects in stuff_object]
                        )
                if pipe.is_start:
                    if scenario == "87" or wall.has_toilet:
                        stuff_object = build_knee_fitting(pipe, riser_projections, material_graph)
                    elif scenario in ["45", "30_15"]:
                        stuff_object = build_knee_fitting_45(pipe, riser_projections, material_graph)
                    mesh_data.extend(obj.data.copy() for obj in stuff_object)
        elif wall.with_riser:
            if not wall.has_toilet:
                riser_obj_p, node = build_otvod_to_knee_pipe(
                    riser_projections_test, walls, wall
                )
                if riser_obj_p:
                    mesh_data.append(riser_obj_p.data.copy())
                    material_graph.add_node(node)
            wall.start_pipe_point = riser_projections
            if len(wall.stuff_point) == 0:
                end = wall.coordinates.start
                for wall_ in walls:
                    if wall_ == wall:
                        continue
                    else:
                        if get_neighbour_wall(wall, wall_):
                            end = get_neighbour_wall(wall, wall_)
                pipes = [
                    Pipe(
                        Segment(wall.start_pipe_point, end),
                        is_start=True,
                        is_end=True,
                        with_riser=True,
                    )
                ]
            else:
                pipes, start_height = count_pipes_for_wall_with_stuff(
                    wall, walls, riser_projections
                )
            # pipes wall
            for idx, pipe in enumerate(pipes):
                if os.getenv("LOCAL_ALGO"):
                    build_pipe_arrows(pipe)
                obj = FITTINGS["d110"] if pipe.is_toilet else FITTINGS["d50"]
                mesh_obj, node = build_pipe_mesh(
                    obj, pipe, scenario
                )
                mesh_data.append(mesh_obj.data.copy())
                material_graph.add_node(node)
                if pipe.is_toilet:
                    toilet_objets = build_toilet_mesh(pipe, material_graph)
                    mesh_data.extend([objects.data.copy() for objects in toilet_objets])
                else:
                    if pipe.stuff:
                        if scenario == "87":
                            stuff_object = build_stuff_mesh_87(pipe, material_graph)
                        elif scenario == "45":
                            stuff_object = build_stuff_mesh_45(pipe, material_graph)
                        elif scenario == "30_15":
                            stuff_object = build_stuff_mesh_30_15(pipe, material_graph)
                        mesh_data.extend(
                            [objects.data.copy() for objects in stuff_object]
                        )
        else:
            if if_wall_in_path_for_riser(wall, walls):
                obj = FITTINGS["d50"]
                pipe_coordinates = (
                    Segment(wall.end, wall.start)
                    if l1_distance(wall.start, riser_projections)
                    < l1_distance(wall.end, riser_projections)
                    else Segment(wall.start, wall.end)
                )
                pipe = Pipe(pipe_coordinates, is_start=True, is_end=True, is_wall_end=True, is_wall_start=True)
                pipe_obj, node = build_pipe_mesh(
                    obj, pipe, scenario
                )
                material_graph.add_node(node)
                if os.getenv("LOCAL_ALGO"):
                    build_pipe_arrows(pipe)

                if scenario == "87" or wall.has_toilet:
                    stuff_object = build_knee_fitting(pipe, riser_projections, material_graph)
                elif scenario in ["45", "30_15"]:
                    stuff_object = build_knee_fitting_45(pipe, riser_projections, material_graph)
                mesh_data.extend(obj.data.copy() for obj in stuff_object)
                objs = [pipe_obj] + stuff_object
                mesh_data.extend([obj.data.copy() for obj in objs])
    return mesh_data, material_graph


def build_path(
    walls, riser_projections, riser_coordinates, scrennshot_name, scenario="87"
):
    mesh_data, material_graph = build_mesh_path(walls, riser_projections, riser_coordinates, scrennshot_name, scenario)
    all_figures, grap_df = process_artifacts(mesh_data, material_graph, scrennshot_name, walls)
    return all_figures, grap_df
