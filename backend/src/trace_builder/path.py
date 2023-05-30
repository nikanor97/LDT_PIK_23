# %%
from src.trace_builder.model import Point, Segment
from src.trace_builder.wall import Wall, Pipe
from src.trace_builder.geometry import is_dot_inside_segment, l1_distance
import re
from typing import List, Tuple
import vtkplotlib as vpl
from stl import mesh

from src.trace_builder.constants import FITTINGS, GLOBAL_INIT_MIN
import math
import numpy as np
from src.trace_builder.manipulate_3d import cutout_pipe, center_pipe


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
    else:
        return False


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


def is_parallel_X(segment: Segment):
    return True if segment.start.y == segment.end.y else False


def is_parallel_Y(segment: Segment):
    return True if segment.start.x == segment.end.x else False


def is_pipe_projection_on_high(segment: Segment, riser_projection: Point):
    return (
        True
        if (segment.start.y < riser_projection.y)
        or (segment.end.y < riser_projection.y)
        else False
    )


def is_pipe_projection_on_right(segment: Segment, riser_projection: Point):
    return (
        True
        if (segment.start.x < riser_projection.x)
        or (segment.end.x < riser_projection.x)
        else False
    )


def load_obj(obj):
    return mesh.Mesh.from_file(obj["path"])


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
    return walls[best_wall]


def count_pipes_for_wall_with_stuff(wall, walls, riser_projections):
    start, end = None, wall.start_pipe_point
    count_sutff = len(wall.stuff_point)
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
    if len(wall.stuff_point) == 1:
        start_end_pipes = [
            Pipe(
                coordinates=Segment(start, end),
                is_toilet=wall.has_toilet,
                with_riser=wall.with_riser,
                is_end=True,
                is_start=True,
                stuff=wall.stuff_point[0],
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
        # start_end_pipes = start_end_pipes[1:] # ¯\_(ツ)_/¯
        if is_last_stuff_is_edged:
            start_end_pipes[-1].is_end = True
            start_end_pipes[0].is_start = True
        else:
            start_end_pipes[0].is_end = True
            start_end_pipes[-1].is_start = True
    min_height = estimate_min_height(wall, riser_projections)
    point = wall.start if wall.start != wall.start_pipe_point else wall.end
    end_wall = get_nearest_wall_to_point(point, wall, walls)
    if end_wall.has_stuff:
        start_end_pipes.append(
            Pipe(
                coordinates=Segment(start_end_pipes[-1].coordinates.start, point),
                is_toilet=False,
                with_riser=False,
                stuff=None,
                is_end=True,
            )
        )
        start_end_pipes[-2].is_end = False
    return start_end_pipes, min_height


def if_wall_in_path_for_riser(wall, walls, riser_projection):
    return False


def wall_with_riser(wall_riser, riser_projections):
    start_end_pipes = []
    end = wall_riser.start
    start = riser_projections
    start_end_pipes.append(Segment(start, end))
    end = wall_riser.end
    start_end_pipes.append(Segment(start, end))
    return start_end_pipes


def build_pipe_mesh(obj, pipe, riser_projections):
    mesh_obj = load_obj(obj)
    pipe_length = l1_distance(pipe.start, pipe.end)
    mesh_obj = center_pipe(mesh_obj, "z")
    mesh_obj = cutout_pipe(mesh_obj, pipe_length)
    if is_parallel_X(pipe):
        if is_pipe_projection_on_right(pipe, riser_projections):
            mesh_obj.rotate([0, 1, 0.0], math.radians(90))
            mesh_obj.x += min(pipe.start.x, pipe.end.x)
        else:
            mesh_obj.rotate([0, 1, 0.0], math.radians(-90))
            mesh_obj.x += max(pipe.start.x, pipe.end.x)
        # mesh_obj = move_pipe(mesh_obj, min(pipe.start.x, pipe.end.x), "x")
        # mesh_obj = move_pipe(mesh_obj, pipe.start.y, "y")
        mesh_obj.y += pipe.start.y
    else:
        if is_pipe_projection_on_high(pipe, riser_projections):
            mesh_obj.rotate([1, 0, 0.0], math.radians(-90))
            mesh_obj.y += min(pipe.start.y, pipe.end.y)
        else:
            mesh_obj.rotate([1, 0, 0.0], math.radians(90))
            mesh_obj.y += max(pipe.start.y, pipe.end.y)
        mesh_obj.x += pipe.start.x
        # mesh_obj.y += min(pipe.start.y, pipe.end.y)
    return mesh_obj


def rotate_troinik_toilet(obj, pipe, is_low=False):
    if is_parallel_X(pipe.coordinates):
        obj.rotate([0, 0, 1], math.radians(90))
        if is_pipe_projection_on_high(pipe.coordinates, pipe.stuff.coordinates):
            obj.rotate([1, 0, 0], math.radians(-90))
            if is_low:
                obj.rotate([1, 0, 0], math.radians(45))  # rotate final angel tee
            else:
                obj.rotate([1, 0, 0], math.radians(-90))  # rotate final angel tee
            if pipe.coordinates.start.x < pipe.coordinates.end.x:
                pass
            else:
                obj.rotate([0, 1, 0], math.radians(180))
        else:
            obj.rotate([1, 0, 0], math.radians(90))
            if is_low:
                obj.rotate([1, 0, 0], math.radians(-45))  # rotate final angel tee
            else:
                obj.rotate([1, 0, 0], math.radians(-90))  # rotate final angel tee
            if pipe.coordinates.start.x < pipe.coordinates.end.x:
                obj.rotate([0, 1, 0], math.radians(180))
            else:
                pass
    else:
        if is_pipe_projection_on_right(pipe.coordinates, pipe.stuff.coordinates):
            obj.rotate([0, 1, 0], math.radians(90))
            if is_low:
                obj.rotate([0, 1, 0], math.radians(-45))  # rotate final angel tee
            else:
                obj.rotate([0, 1, 0], math.radians(-90))  # rotate final angel tee
            if pipe.coordinates.start.y > pipe.coordinates.end.y:
                pass
            else:
                obj.rotate([1, 0.0], math.radians(180))
        else:
            obj.rotate([0, 1, 0], math.radians(-90))
            if is_low:
                obj.rotate([0, 1, 0], math.radians(45))  # rotate final angel tee
            else:
                obj.rotate([0, 1, 0], math.radians(90))  # rotate final angel tee
            if pipe.coordinates.start.y > pipe.coordinates.end.y:
                # obj.rotate([1,0,0],math.radians(180))
                pass
            else:
                obj.rotate([1, 0, 0], math.radians(180))
    return obj


def rotate_reduction(obj, pipe):
    if is_parallel_X(pipe.coordinates):
        if pipe.coordinates.start.x < pipe.coordinates.end.x:
            obj.rotate([1, 0, 0], math.radians(-90))
            obj.rotate([0, 0, 1], math.radians(90))
            obj.y -= 0
            obj.x -= 250
        else:
            obj.rotate([1, 0, 0], math.radians(-90))
            obj.rotate([0, 1, 0], math.radians(-90))
            obj.y += 250
    else:
        if pipe.coordinates.start.y > pipe.coordinates.end.y:
            obj.rotate([1, 0, 0], math.radians(-90))
            obj.rotate([0, 1, 0], math.radians(180))
            obj.y += 250
        else:
            obj.rotate([1, 0, 0], math.radians(-90))
            obj.y -= 250
    return obj


def rotate_otvod(obj, pipe):
    if is_parallel_X(pipe.coordinates):
        obj.rotate([0, 1, 0], math.radians(-90))
        if is_pipe_projection_on_high(pipe.coordinates, pipe.stuff.coordinates):
            obj.rotate([0, 1, 0], math.radians(90))
            obj.rotate([1, 0, 0], math.radians(90))
        else:
            obj.rotate([1, 0, 0], math.radians(90))
            obj.rotate([0, 0, 1], math.radians(90))
    else:
        if is_pipe_projection_on_right(pipe.coordinates, pipe.stuff.coordinates):
            obj.rotate([1, 0, 0], math.radians(90))
            obj.rotate([0, 0, 1], math.radians(90))
            pass
        else:
            obj.rotate([0, 0, 1], math.radians(-90))
            obj.rotate([0, 1, 0], math.radians(90))
            # obj.rotate([1,0,0], math.radians(180))
            pass
    return obj


def rotate_otvod_low(obj, pipe, low=False):
    if is_parallel_X(pipe.coordinates):
        if pipe.coordinates.start.x < pipe.coordinates.end.x:
            # CHECKED
            obj.rotate([0, 0, 1], math.radians(90))
            if low:
                obj.rotate([1, 0, 0], math.radians(-45))
        else:
            # CHECKED
            obj.rotate([0, 0, 1], math.radians(-90))
            if low:
                obj.rotate([1, 0, 0], math.radians(45))
    else:
        if pipe.coordinates.start.y < pipe.coordinates.end.y:
            # CHECKED
            if low:
                obj.rotate([0, 1, 0], math.radians(45))
            pass
        else:
            if low:
                obj.rotate([0, 1, 0], math.radians(-45))
            # CHECKED
            obj.rotate([0, 0, 1], math.radians(180))
    return obj


def shift_rotate_low(obj, pipe, diameter=50, low=False):
    bias_1 = 60 if diameter == 110 else 30
    bias_2 = 65 if diameter == 110 else 80
    if is_parallel_X(pipe.coordinates):
        obj.x += bias_1
    else:
        obj.y += bias_1
    obj.z += bias_2
    return obj


def shift_otvod(obj, pipe, diameter=110):
    bias_1 = 220 if diameter == 110 else 80
    bias_2 = 60 if diameter == 110 else 0
    bias_3 = 130 if diameter == 110 else 65
    if is_parallel_X(pipe.coordinates):
        if is_pipe_projection_on_high(pipe.coordinates, pipe.stuff.coordinates):
            obj.y += bias_1
            obj.x -= bias_2
        else:
            obj.y -= bias_1
            obj.x -= bias_2
    else:
        if is_pipe_projection_on_right(pipe.coordinates, pipe.stuff.coordinates):
            obj.x += bias_1
            obj.y -= bias_2
        else:
            obj.x -= bias_1
            obj.y -= bias_2
    obj.z += bias_3
    return obj


def build_toilet_mesh(pipe: Pipe):
    mesh_objs = []
    if pipe.is_end:
        obj = load_obj(FITTINGS["otvod_110x87"])
        obj = rotate_otvod_low(obj, pipe, low=True)
        obj = shift_rotate_low(obj, pipe, 110)
        obj.x -= 85
    else:
        obj = load_obj(FITTINGS["troinik_110_110x87"])
        obj_reduction = load_obj(FITTINGS["reduction"])
        obj_reduction = rotate_reduction(obj_reduction, pipe)
        obj_reduction.x += pipe.coordinates.start.x
        obj_reduction.y += pipe.coordinates.start.y
        obj = rotate_troinik_toilet(obj, pipe, is_low=True)
        mesh_objs.append(obj_reduction)

    obj_otvod = load_obj(FITTINGS["otvod_110x45"])
    obj_otvod = rotate_otvod(obj_otvod, pipe)
    obj_otvod = shift_otvod(obj_otvod, pipe)
    obj_otvod.x += pipe.coordinates.start.x
    obj_otvod.y += pipe.coordinates.start.y
    mesh_objs.append(obj_otvod)
    # obj = rotate_troinik_toilet(obj, pipe, is_low=True)
    obj.x += pipe.coordinates.start.x
    obj.y += pipe.coordinates.start.y
    if pipe.coordinates.start.y < pipe.coordinates.end.y:
        obj.y -= 125
    if pipe.coordinates.start.x < pipe.coordinates.end.x:
        obj.x -= 125

    mesh_objs.append(obj)
    return mesh_objs


def build_stuff_mesh(pipe: Pipe):
    meshes = []
    if pipe.is_end:
        troinik = load_obj(FITTINGS["otvod_50x87"])
        troinik = rotate_otvod_low(troinik, pipe)
        troinik = shift_rotate_low(troinik, pipe, 50)
        # TODO
    else:
        troinik = load_obj(FITTINGS["troinik_50_50x87"])
        troinik = rotate_troinik_toilet(troinik, pipe)
    troinik.x += pipe.coordinates.start.x
    troinik.y += pipe.coordinates.start.y
    bias = 100

    straight_obj = load_obj(FITTINGS["d50"])
    straight_obj = center_pipe(straight_obj, "z")
    straight_obj = cutout_pipe(straight_obj, pipe.stuff.height)
    straight_obj.x += pipe.coordinates.start.x
    straight_obj.y += pipe.coordinates.start.y
    straight_obj.z += pipe.stuff.height

    otvod = load_obj(FITTINGS["otvod_50x87"])
    otvod = rotate_otvod(otvod, pipe)
    shift_otvod(otvod, pipe, 50)
    otvod.x += pipe.coordinates.start.x
    # otvod.x -= 80
    otvod.y += pipe.coordinates.start.y
    otvod.z += pipe.stuff.height

    if pipe.coordinates.start.y < pipe.coordinates.end.y:
        troinik.y -= bias
        straight_obj.y -= bias - 30
        otvod.y -= bias - 30
    if pipe.coordinates.start.x < pipe.coordinates.end.x:
        troinik.x -= bias
        straight_obj.x -= bias - 30
        otvod.x -= bias - 30

    meshes = [straight_obj, troinik, otvod]
    return meshes


def rotate_otvod_link_knee(obj, pipe, riser_projections, diameter=110):
    bias_1 = 160 if diameter == 110 else 130
    bias_2 = 37 if diameter == 110 else 17
    if is_parallel_X(pipe.coordinates):
        if pipe.coordinates.end.y > riser_projections.y:  # pipe above riser
            if pipe.coordinates.start.x < pipe.coordinates.end.x:  # right
                obj.rotate([0, 0, 1], math.radians(180))
                obj.rotate([0, 1, 0], math.radians(90))
                obj.y += bias_2
                obj.x -= bias_1 - 37
            else:
                obj.rotate([0, 0, 1], math.radians(180))
                obj.rotate([0, 1, 0], math.radians(-90))
                obj.x += bias_1 - 37
                obj.y += bias_2
        else:
            if pipe.coordinates.start.x < pipe.coordinates.end.x:  # right
                obj.rotate([0, 1, 0], math.radians(90))
                obj.x -= bias_1
            else:
                obj.rotate([0, 1, 0], math.radians(-90))
                obj.x += bias_1 - 50
    else:
        # CHECKED
        if pipe.coordinates.end.x < riser_projections.x:  # pipe -> riser
            if pipe.coordinates.start.y < pipe.coordinates.end.y:  # up
                obj.rotate([0, 0, 1], math.radians(90))
                obj.rotate([1, 0, 0], math.radians(-90))
                obj.y -= bias_1
            else:
                obj.rotate([0, 0, 1], math.radians(90))
                obj.rotate([1, 0, 0], math.radians(90))
        else:  # riser -> pipe
            # CHECKED
            if pipe.coordinates.start.y < pipe.coordinates.end.y:  # up
                obj.rotate([1, 0, 0], math.radians(-90))
                obj.rotate([0, 1, 0], math.radians(90))
                obj.y -= bias_1
            else:
                obj.rotate([0, 0, 1], math.radians(-90))
                obj.rotate([1, 0, 0], math.radians(90))
    return obj


def build_knee_fitting(pipe, riser_projections):
    fitting_meta = (
        FITTINGS["otvod_110x87"] if pipe.is_toilet else FITTINGS["otvod_50x87"]
    )
    diameter = 110 if pipe.is_toilet else 50
    obj = load_obj(fitting_meta)
    obj = rotate_otvod_link_knee(obj, pipe, riser_projections, diameter)
    obj.x += pipe.coordinates.end.x
    obj.y += pipe.coordinates.end.y
    return obj


def build_riser(riser_coordinates, riser_projections, walls):
    fitting_meta = FITTINGS["troinik_110_110x87"]
    obj = load_obj(fitting_meta)
    obj = rotate_riser(obj, riser_coordinates, riser_projections, walls)
    obj.x += riser_coordinates.x
    obj.y += riser_coordinates.y
    obj.z += 60
    return obj


def rotate_riser(obj, riser_coordinates, riser_projections, walls):
    if riser_projections.y > riser_coordinates.y:  # turn up
        obj.rotate([1, 0, 0], math.radians(-90))
        obj.y -= 50
    elif riser_projections.y < riser_coordinates.y:  # turn down
        obj.rotate([1, 0, 0], math.radians(-90))
        obj.rotate([0, 0, 1], math.radians(180))
    elif riser_projections.x < riser_coordinates.x:  # turn left
        obj.rotate([1, 0, 0], math.radians(-90))
        obj.rotate([0, 0, 1], math.radians(-90))
    else:  # turn right
        obj.rotate([1, 0, 0], math.radians(-90))
        obj.rotate([0, 0, 1], math.radians(90))

    # TEST
    # obj.x -= 500
    # obj.y -= 500
    return obj


def build_riser_otvod(riser_coordinates, riser_projections, walls):
    toilet_coordinates = get_toilet_coordinates_form_wall(walls)
    pipe = "right"
    # fitting_meta = FITTINGS["otvod_110x87"]
    fitting_meta = FITTINGS["otvod_110_50_87_back"]
    obj = load_obj(fitting_meta)
    fix_legnt, common_bias = 100, 10
    y_bias = 120
    x_bias = 0
    ###
    if riser_projections.y > riser_coordinates.y:  # up
        if toilet_coordinates.x > riser_projections.x:  # toilet on right
            pipe_ = "up right"
            pipe = Pipe(
                Segment(
                    start=Point(
                        toilet_coordinates.x + fix_legnt,
                        riser_projections.y + fix_legnt,
                    ),
                    end=Point(toilet_coordinates.x, riser_projections.y + fix_legnt),
                )
            )
            y_bias = -40
        else:
            pipe_ = "up left"
            pipe = Pipe(
                Segment(
                    start=Point(
                        toilet_coordinates.x - fix_legnt - common_bias,
                        riser_projections.y + fix_legnt,
                    ),
                    end=Point(
                        toilet_coordinates.x - common_bias,
                        riser_projections.y + fix_legnt,
                    ),
                )
            )
            y_bias = -40
    elif riser_projections.y < riser_coordinates.y:  # down
        if not toilet_coordinates.x > riser_projections.x:  # toilet on right
            pipe_ = "down right"
            pipe = Pipe(
                Segment(
                    start=Point(
                        toilet_coordinates.x + fix_legnt + common_bias,
                        riser_projections.y,
                    ),
                    end=Point(toilet_coordinates.x + common_bias, riser_projections.y),
                )
            )
            y_bias = -160
            x_bias = 10
        else:
            pipe_ = "down left"
            pipe = Pipe(
                Segment(
                    start=Point(
                        toilet_coordinates.x - fix_legnt - common_bias,
                        riser_projections.y,
                    ),
                    end=Point(toilet_coordinates.x - common_bias, riser_projections.y),
                )
            )
            y_bias = -180
            x_bias = 40
    elif riser_projections.x < riser_coordinates.x:  # left
        if toilet_coordinates.y > riser_projections.y:  # toilet on up
            pipe_ = "left up"
            pipe = Pipe(
                Segment(
                    start=Point(
                        riser_projections.x - fix_legnt,
                        toilet_coordinates.y + fix_legnt,
                    ),
                    end=Point(riser_projections.x - fix_legnt, toilet_coordinates.y),
                )
            )
            y_bias = 120
            x_bias = -150
        else:
            pipe_ = "left down"
            pipe = Pipe(
                Segment(
                    start=Point(
                        riser_projections.x - fix_legnt,
                        toilet_coordinates.y - fix_legnt,
                    ),
                    end=Point(riser_projections.x - fix_legnt, toilet_coordinates.y),
                )
            )
            y_bias = 20
            x_bias = 0
    else:  # right
        if toilet_coordinates.y > riser_projections.y:  # toilet on up
            pipe_ = "right up"
            pipe = Pipe(
                Segment(
                    start=Point(
                        riser_projections.x + fix_legnt,
                        toilet_coordinates.y + fix_legnt,
                    ),
                    end=Point(riser_projections.x + fix_legnt, toilet_coordinates.y),
                )
            )
            y_bias = 120
            x_bias = 180
        else:
            pipe_ = "right down"
            pipe = Pipe(
                Segment(
                    start=Point(
                        riser_projections.x + fix_legnt,
                        toilet_coordinates.y - fix_legnt,
                    ),
                    end=Point(riser_projections.x + fix_legnt, toilet_coordinates.y),
                )
            )
            y_bias = 40
            x_bias = 150
    # print(pipe_)
    obj = rotate_otvod_link_knee(obj, pipe, riser_projections, 110)
    obj.x += riser_projections.x
    obj.y += riser_projections.y
    obj.y += y_bias
    obj.x += x_bias
    return obj


def build_riser_to_otvod_pipe(riser_coordinates, riser_projections, treshold=200):
    bias1 = 0
    bias2 = 0
    if (
        riser_coordinates.y <= riser_projections.y - treshold
    ):  # proj higher more than 200
        riser_projection_ = riser_coordinates
        pipe = Pipe(
            Segment(
                start=Point(riser_projections.x, riser_projections.y),
                end=Point(riser_projections.x, riser_coordinates.y),
            )
        )
        bias2 = -70
    elif (
        riser_coordinates.y - treshold >= riser_projections.y
    ):  # proj lower more than 200
        riser_projection_ = riser_coordinates
        pipe = Pipe(
            Segment(
                start=Point(riser_projections.x, riser_projections.y),
                end=Point(riser_projections.x, riser_coordinates.y),
            )
        )
        bias2 = -60

    elif (
        riser_coordinates.x - treshold >= riser_projections.x
    ):  # proj left more than 200
        riser_projection_ = riser_coordinates
        pipe = Pipe(
            Segment(
                start=Point(riser_coordinates.x, riser_projections.y),
                end=Point(riser_projections.x, riser_coordinates.y),
            )
        )
        bias1 = -60
    elif (
        riser_projections.x - treshold >= riser_coordinates.x
    ):  # proj right more than 200
        riser_projection_ = riser_coordinates
        pipe = Pipe(
            Segment(
                start=Point(riser_coordinates.x, riser_projections.y),
                end=Point(riser_projections.x, riser_coordinates.y),
            )
        )
        bias1 = 60
    else:
        return None
    obj = build_pipe_mesh(FITTINGS["d110"], pipe.coordinates, riser_projection_)
    obj.x += bias1
    obj.y += bias2
    return obj


def build_otvod_to_knee_pipe(riser_projections, walls, riser_wall):
    bias_x, bias_y = 0, 0
    toilet_coordinates = get_toilet_coordinates_form_wall(walls)

    if riser_projections.x <= (toilet_coordinates.x - 200) and is_parallel_X(
        riser_wall.coordinates
    ):
        pipe = Pipe(
            Segment(
                start=Point(toilet_coordinates.x - 30, riser_projections.y),
                end=Point(riser_projections.x + 30, riser_projections.y),
            )
        )
        # bias_x = 60
    elif (riser_projections.x - 200) >= toilet_coordinates.x and is_parallel_X(
        riser_wall.coordinates
    ):
        pipe = Pipe(
            Segment(
                start=Point(riser_projections.x - 30, riser_projections.y),
                end=Point(toilet_coordinates.x + 30, riser_projections.y),
            )
        )
    elif (riser_projections.y - 200) >= toilet_coordinates.y and is_parallel_Y(
        riser_wall.coordinates
    ):
        pipe = Pipe(
            Segment(
                start=Point(riser_projections.x, toilet_coordinates.y + 30),
                end=Point(riser_projections.x, toilet_coordinates.y - 30),
            )
        )
    elif riser_projections.y <= (toilet_coordinates.y - 200) and is_parallel_Y(
        riser_wall.coordinates
    ):
        pipe = Pipe(
            Segment(
                start=Point(riser_projections.x, toilet_coordinates.y - 30),
                end=Point(riser_projections.x, riser_projections.y + 30),
            )
        )
        # bias_x = 60
    else:
        return None
    obj = build_pipe_mesh(FITTINGS["d110"], pipe.coordinates, riser_projections)
    obj.x += bias_x
    obj.y += bias_y
    return obj


def get_toilet_coordinates_form_wall(walls):
    for wall in walls:
        if wall.has_toilet:
            for stuff in wall.stuff_point:
                if stuff.is_toilet:
                    return stuff.coordinates
    return None


# %%
def build_path(walls, riser_projections, riser_coordinates, scrennshot_name):
    mesh_data = []
    # riser_coordinates.y -= 200
    bi = 0
    print(riser_coordinates.x)
    riser_coordinates_test = Point(riser_coordinates.x + bi, riser_coordinates.y + bi)
    riser_projections_test = Point(riser_projections.x + bi, riser_projections.y + bi)
    # riser_coordinates_test.y -= 1000
    # riser_coordinates_test.x -= 900
    # riser_projections_test.x -= 900
    # riser_projections_test.y -= 400
    # riser_projections_test.y  = riser_coordinates_test.y
    riser_obj = build_riser(
        riser_coordinates_test, riser_projections_test, walls
    ).data.copy()
    # riser_obj = build_riser(riser_coordinates, riser_projections, walls).data.copy()
    mesh_data.append(riser_obj)
    riser_obj_p = build_riser_to_otvod_pipe(
        riser_coordinates_test, riser_projections_test
    )
    if riser_obj_p:
        mesh_data.append(riser_obj_p.data.copy())
    # pipe_turn = build_riser_pipes(riser_coordinates, riser_projections, walls).data.copy()
    pipe_turn = build_riser_otvod(
        riser_coordinates_test, riser_projections_test, walls
    ).data.copy()
    mesh_data.append(pipe_turn)
    for wall in walls:
        obj = FITTINGS["d50"]
        if not wall.with_riser and wall.has_stuff:
            # TODO move end for enable right turn
            pipes, start_height = count_pipes_for_wall_with_stuff(
                wall, walls, riser_projections
            )
            for idx, pipe in enumerate(pipes):
                obj = FITTINGS["d110"] if pipe.is_toilet else FITTINGS["d50"]
                mesh_obj = build_pipe_mesh(obj, pipe.coordinates, riser_projections)
                if pipe.is_toilet:
                    toilet_objets = build_toilet_mesh(pipe)
                    mesh_data.extend([objects.data.copy() for objects in toilet_objets])
                else:
                    if pipe.stuff:
                        stuff_object = build_stuff_mesh(pipe)
                        mesh_data.extend(
                            [objects.data.copy() for objects in stuff_object]
                        )
                if pipe.is_start:
                    knee_obj = build_knee_fitting(pipe, riser_projections).data.copy()
                    mesh_data.append(knee_obj)
                mesh_data.append(mesh_obj.data.copy())
        elif wall.with_riser:
            # pipes for whole wall
            # pipes = wall_with_riser(wall, riser_projections)
            # for idx, pipe in enumerate(pipes):
            #     mesh_obj = build_pipe_mesh(obj, pipe, riser_projections)
            #     mesh_data.append(mesh_obj.data.copy())
            if not wall.has_toilet:
                riser_obj_p = build_otvod_to_knee_pipe(
                    riser_projections_test, walls, wall
                )
                if riser_obj_p:
                    mesh_data.append(riser_obj_p.data.copy())
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
                obj = FITTINGS["d110"] if pipe.is_toilet else FITTINGS["d50"]
                mesh_obj = build_pipe_mesh(obj, pipe.coordinates, riser_projections)
                if pipe.is_toilet:
                    toilet_objets = build_toilet_mesh(pipe)
                    mesh_data.extend([objects.data.copy() for objects in toilet_objets])
                else:
                    if pipe.stuff:
                        stuff_object = build_stuff_mesh(pipe)
                        mesh_data.extend(
                            [objects.data.copy() for objects in stuff_object]
                        )
                mesh_data.append(mesh_obj.data.copy())
        else:
            if_wall_in_path_for_riser(wall, walls, riser_projections)
    all_figures = mesh.Mesh(np.concatenate(mesh_data))
    all_figures = mesh.Mesh(np.concatenate(mesh_data))
    vpl.mesh_plot(all_figures)
    vpl.save_fig(scrennshot_name, pixels=(1920,1080), off_screen=True)
    # vpl.mesh_plot(all_figures)
    # vpl.show()
    return all_figures
