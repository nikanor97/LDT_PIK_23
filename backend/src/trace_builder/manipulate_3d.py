import math
from typing import Any

import numpy as np
import vtkplotlib as vpl
from src.trace_builder.constants import FITTINGS, REDUCTION_SHIFT
from src.trace_builder.geometry import is_parallel_X, is_parallel_Y, l1_distance
from src.trace_builder.graph_models import Node, PipeGraph
from src.trace_builder.mesh_3d.common import (
    draw_letter,
    shift_knee_for_slope,
    shift_pipe_for_slope,
    shift_stuff_after_reduction,
)
from src.trace_builder.model import Point, Segment
from src.trace_builder.models import Pipe, Wall
from stl import mesh


def cutout_pipe(pipe, length=10):
    x, y, z = pipe.vectors.reshape((-1, 3)).T
    if min(z) > (-length):
        mask = z < -100
    else:
        mask = z < (-length)
    start = max(z)
    curr_length = max(z) - min(z)
    if length < curr_length:
        z[mask] = start - length
    else:
        z[mask] = z[mask] - np.abs(length - curr_length)
    cutted = np.vstack([x, y, z]).reshape(3, -1, 3).T
    clutted_pipe = np.zeros((cutted.shape[1], 3, 3))
    for i in range(cutted.shape[1]):
        clutted_pipe[i] = cutted[:, i, :]
    pipe.vectors = clutted_pipe
    return pipe


def center_pipe(pipe, axis="x"):
    axis_mapper = {"x": 0, "y": 1, "z": 2}
    axis_values = pipe.vectors.reshape((-1, 3)).T
    # min_value = max(axis_values[axis_mapper[axis]])
    min_value = min(axis_values[axis_mapper[axis]])
    # axis_values[axis_mapper[axis]] += min_value-50
    # axis_values[axis_mapper[axis]] -= (min_value - 25)
    axis_values[axis_mapper[axis]] += min_value
    cutted = np.vstack(axis_values).reshape(3, -1, 3).T
    centered_pipe = np.zeros((cutted.shape[1], 3, 3))
    for i in range(cutted.shape[1]):
        centered_pipe[i] = cutted[:, i, :]
    pipe.vectors = centered_pipe
    return pipe


def move_pipe(pipe, value, axis="z"):
    axis_mapper = {"x": 0, "y": 1, "z": 2}
    axis_values = pipe.vectors.reshape((-1, 3)).T
    axis_values[axis_mapper[axis]] += value
    cutted = np.vstack(axis_values).reshape(3, -1, 3).T
    centered_pipe = np.zeros((cutted.shape[1], 3, 3))
    for i in range(cutted.shape[1]):
        centered_pipe[i] = cutted[:, i, :]
    pipe.vectors = centered_pipe
    return pipe


def cutout_pipe_end(pipe, how_much_cutoff=10):
    x, y, z = pipe.vectors.reshape((-1, 3)).T
    # mask = z < -100
    mask = z < max(z) - 137
    z[mask] = min(z) + how_much_cutoff
    cutted = np.vstack([x, y, z]).reshape(3, -1, 3).T
    clutted_pipe = np.zeros((cutted.shape[1], 3, 3))
    for i in range(cutted.shape[1]):
        clutted_pipe[i] = cutted[:, i, :]
    pipe.vectors = clutted_pipe
    return pipe


def load_obj(obj):
    return mesh.Mesh.from_file(obj["path"])


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


def get_toilet_coordinates_form_wall(walls):
    for wall in walls:
        if wall.has_toilet:
            for stuff in wall.stuff_point:
                if stuff.is_toilet:
                    return stuff.coordinates
    return None


def get_translation_matrix(x_shift, y_shift, z_shift):
    """
    Returns a 4x4 translation matrix to shift a point by (x_shift, y_shift, z_shift)
    """
    return np.array(
        [[1, 0, 0, x_shift], [0, 1, 0, y_shift], [0, 0, 1, z_shift], [0, 0, 0, 1]]
    )


def get_rotation_matrix(x_rotation, y_rotation, z_rotation):
    """
    Returns a 4x4 rotation matrix to rotate a point by (x_rotation, y_rotation, z_rotation) in degrees
    """
    x_rotation = np.radians(x_rotation)
    y_rotation = np.radians(y_rotation)
    z_rotation = np.radians(z_rotation)

    Rx = np.array(
        [
            [1, 0, 0],
            [0, np.cos(x_rotation), -np.sin(x_rotation)],
            [0, np.sin(x_rotation), np.cos(x_rotation)],
        ]
    )

    Ry = np.array(
        [
            [np.cos(y_rotation), 0, np.sin(y_rotation)],
            [0, 1, 0],
            [-np.sin(y_rotation), 0, np.cos(y_rotation)],
        ]
    )

    Rz = np.array(
        [
            [np.cos(z_rotation), -np.sin(z_rotation), 0],
            [np.sin(z_rotation), np.cos(z_rotation), 0],
            [0, 0, 1],
        ]
    )

    R = Rx.dot(Ry).dot(Rz)
    return np.vstack([np.hstack([R, np.zeros((3, 1))]), [0, 0, 0, 1]])


def transform_mesh(
    mesh, x_shift=0, y_shift=0, z_shift=0, x_rotation=0, y_rotation=0, z_rotation=0
):
    """
    Applies a 3D transformation to a numpy-stl Mesh object using translation and rotation matrices.
    """

    # Extract the vertex coordinates from the mesh into a numpy array with shape (n, 3)
    vertices = np.hstack(
        [mesh.x.reshape(-1, 1), mesh.y.reshape(-1, 1), mesh.z.reshape(-1, 1)]
    )

    # Apply the transformation to all vertices using the transform() function and matrix multiplication
    T = get_translation_matrix(x_shift, y_shift, z_shift)
    R = get_rotation_matrix(x_rotation, y_rotation, z_rotation)

    homog_points = np.hstack([vertices, np.ones((len(vertices), 1))])
    transformed_points = (T.dot(R).dot(homog_points.T)).T[:, :3]

    # Replace the mesh's vertex coordinates with the transformed vertices
    mesh.points = transformed_points.reshape(-1, 9)
    # mesh.v0[:, :3] = transformed_points[:mesh.v0.shape[0], :]
    # mesh.v1[:, :3] = transformed_points[mesh.v0.shape[0]:2*mesh.v0.shape[0], :]
    # mesh.v2[:, :3] = transformed_points[2*mesh.v0.shape[0]:, :]

    return mesh


def cutout_pipe_obj_v2(obj: Any, obj_meta: dict, pipe: Pipe, scenario: str):
    if pipe.is_wall_start and not pipe.with_riser:
        if scenario in ["45", "30_15"]:
            cutout_pipe_end(obj, 80)
        else:
            cutout_pipe_end(obj, 30)
    if pipe.is_wall_end:
        move_pipe(obj, -80, "z")
        cutout_pipe_end(obj, 80)
    elif pipe.is_end:
        move_pipe(obj, -50, "z")
        cutout_pipe_end(obj, 30)
    else:
        move_pipe(obj, -130, "z")
        cutout_pipe_end(obj, 130)
    return obj


def build_pipe_mesh(
    obj,
    pipe,
    scenario="87",
    cut_lenght=0,
):
    shift_start = 30
    bottleneck_bias = 37
    mesh_obj = load_obj(obj)
    pipe_segment = pipe.coordinates
    pipe_length = l1_distance(pipe_segment.start, pipe_segment.end)
    mesh_obj = center_pipe(mesh_obj, "z")
    cutout_pipe(mesh_obj, pipe_length + bottleneck_bias)
    if obj["diameter"] == 110:
        mesh_obj = cutout_pipe(mesh_obj, pipe_length - cut_lenght)
        move_pipe(mesh_obj, -20, "z")
        cutout_pipe_end(mesh_obj, 20)
    else:
        # mesh_obj = cutout_pipe_obj(mesh_obj, obj, pipe, scenario, shift_start, shift_end)
        mesh_obj = cutout_pipe_obj_v2(mesh_obj, obj, pipe, scenario)
    if is_parallel_X(pipe_segment):
        # if is_pipe_projection_on_right(pipe, riser_projections):
        if pipe_segment.start.x < pipe_segment.end.x:
            mesh_obj.rotate([0, 1, 0], math.radians(90))
            mesh_obj.rotate([0, 1, 0], math.radians(-1.14))
            mesh_obj.x += min(pipe_segment.start.x, pipe_segment.end.x)
        else:
            mesh_obj.rotate([0, 1, 0], math.radians(-90))
            mesh_obj.rotate([0, 1, 0], math.radians(1.14))
            mesh_obj.x += max(pipe_segment.start.x, pipe_segment.end.x)
        mesh_obj.y += pipe_segment.start.y
    else:
        if pipe_segment.start.y < pipe_segment.end.y:
            mesh_obj.rotate([1, 0, 0], math.radians(-90))
            mesh_obj.rotate([1, 0, 0], math.radians(1.14))
            mesh_obj.y += min(pipe_segment.start.y, pipe_segment.end.y)
        else:
            mesh_obj.rotate([1, 0, 0], math.radians(90))
            mesh_obj.rotate([1, 0, 0], math.radians(-1.14))
            mesh_obj.y += max(pipe_segment.start.y, pipe_segment.end.y)
        mesh_obj.x += pipe_segment.start.x
        # mesh_obj.y += min(pipe_segment.start.y, pipe_segment.end.y)
    shift_stuff_after_reduction(mesh_obj, pipe, obj["diameter"])
    shift_pipe_for_slope(mesh_obj, pipe)
    node = Node(obj["name"], obj["id"], pipe_length)
    return mesh_obj, node


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
            obj.rotate([1, 0, 0], math.radians(-1.14))
            obj.y -= 0
            obj.x -= 250
        else:
            obj.rotate([1, 0, 0], math.radians(-90))
            obj.rotate([0, 1, 0], math.radians(-90))
            obj.rotate([1, 0, 0], math.radians(1.14))
            obj.y += 250
    else:
        if pipe.coordinates.start.y > pipe.coordinates.end.y:
            obj.rotate([1, 0, 0], math.radians(-90))
            obj.rotate([0, 1, 0], math.radians(180))
            obj.rotate([1, 0, 0], math.radians(-1.14))
            obj.y += 250
        else:
            obj.rotate([1, 0, 0], math.radians(-90))
            obj.rotate([1, 0, 0], math.radians(1.14))
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


def build_toilet_mesh(pipe: Pipe, material_graph: PipeGraph):
    mesh_objs = []
    nodes = []
    if pipe.is_end:
        obj = load_obj(FITTINGS["otvod_110x87"])
        obj = rotate_otvod_low(obj, pipe, low=True)
        obj = shift_rotate_low(obj, pipe, 110)
        obj.x -= 85
        obj.z += 20
        nodes.append(
            Node(FITTINGS["otvod_110x87"]["name"], FITTINGS["otvod_110x87"]["id"])
        )
    else:
        obj = load_obj(FITTINGS["troinik_110_110x87"])
        obj_reduction = load_obj(FITTINGS["reduction"])
        obj_reduction = rotate_reduction(obj_reduction, pipe)
        obj_reduction.x += pipe.coordinates.start.x
        obj_reduction.y += pipe.coordinates.start.y
        obj_reduction.z -= REDUCTION_SHIFT
        obj = rotate_troinik_toilet(obj, pipe, is_low=True)
        mesh_objs.append(obj_reduction)
        nodes.append(
            Node(
                FITTINGS["troinik_110_110x87"]["name"],
                FITTINGS["otvod_110x87"]["id"],
                is_troinik=True,
            )
        )
        nodes.append(
            Node(
                FITTINGS["reduction"]["name"],
                FITTINGS["otvod_110x87"]["id"],
                is_inside_troinik=True,
            )
        )

    obj_otvod = load_obj(FITTINGS["otvod_110x45"])
    obj_otvod = rotate_otvod(obj_otvod, pipe)
    obj_otvod = shift_otvod(obj_otvod, pipe)
    obj_otvod.x += pipe.coordinates.start.x
    obj_otvod.y += pipe.coordinates.start.y
    mesh_objs.append(obj_otvod)
    nodes.append(
        Node(
            FITTINGS["otvod_110x87"]["name"],
            FITTINGS["otvod_110x87"]["id"],
            is_inside_troinik=True,
            is_end=True,
        )
    )
    # obj = rotate_troinik_toilet(obj, pipe, is_low=True)
    obj.x += pipe.coordinates.start.x
    obj.y += pipe.coordinates.start.y
    if pipe.coordinates.start.y < pipe.coordinates.end.y:
        obj.y -= 125
    if pipe.coordinates.start.x < pipe.coordinates.end.x:
        obj.x -= 125

    mesh_objs.append(obj)
    shift_pipe_for_slope(mesh_objs, pipe)
    material_graph.add_node(nodes, end=True)
    return mesh_objs


def rotate_otvod_45_low(obj, pipe, bias=50):
    if is_parallel_X(pipe.coordinates):
        obj.rotate([0, 0, 1], math.radians(-90))
        obj.rotate([0, 1, 0], math.radians(-45))
        if pipe.coordinates.start.x > pipe.coordinates.end.x:  # stream to left
            obj.x += bias
        else:  # stream to right
            obj.rotate([0, 0, 1], math.radians(180))
            obj.x -= bias
    else:
        obj.rotate([1, 0, 0], math.radians(-45))
        if pipe.coordinates.start.y > pipe.coordinates.end.y:  # stream to down
            obj.rotate([0, 0, 1], math.radians(180))
            obj.y += bias
        else:  # stream to up
            obj.y -= bias
    obj.z += 45
    return obj


def rotate_otvod_45_lower_first(obj, pipe, cum_z, bias=90):
    # transform_mesh(obj)
    bias_1, bias_z = bias, 120 + cum_z
    if is_parallel_X(pipe.coordinates):
        obj.rotate([0, 0, 1], math.radians(-90))
        if pipe.coordinates.start.x > pipe.coordinates.end.x:  # stream to left
            obj.x += bias_1
            obj.z += bias_z
            pass
        else:  # stream to right
            obj.rotate([0, 0, 1], math.radians(180))
            obj.x -= bias_1
            obj.z += bias_z
    else:
        # obj.rotate([1, 0, 0], math.radians(90))
        if pipe.coordinates.start.y > pipe.coordinates.end.y:  # stream to down
            obj.rotate([0, 0, 1], math.radians(180))
            obj.z += bias_z
            obj.y += bias_1
        else:  # stream to up
            obj.y -= bias_1
            obj.z += bias_z
    return obj


def shift_straight_pipe_45(obj, pipe, cum_z, bias=90):
    obj.z += cum_z
    bias_1 = bias
    if is_parallel_X(pipe.coordinates):
        if pipe.coordinates.start.x > pipe.coordinates.end.x:  # stream to left
            obj.x += bias_1
        else:  # stream to right
            obj.x -= bias_1
    else:
        if pipe.coordinates.start.y > pipe.coordinates.end.y:  # stream to up
            obj.y += bias_1
        else:  # stream to left
            obj.y -= bias_1
    return obj


def rotate_otvod_45_upper_first(obj, pipe, cum_z=0, bias=90):
    bias_1, bias_2 = bias, 45
    if is_parallel_X(pipe.coordinates):
        obj.rotate([0, 0, 1], math.radians(180))
        obj.rotate([1, 0, 0], math.radians(-45))
        if pipe.coordinates.start.y > pipe.stuff.coordinates.y:
            pass
            obj.y -= bias_2
        else:
            obj.rotate([0, 0, 1], math.radians(180))
            obj.y += bias_2

        if pipe.coordinates.start.x > pipe.coordinates.end.x:
            obj.x += bias_1
        else:
            obj.x -= bias_1
    else:
        obj.rotate([0, 0, 1], math.radians(-90))
        obj.rotate([0, 1, 0], math.radians(45))
        if pipe.coordinates.start.x > pipe.stuff.coordinates.x:
            obj.x -= 40
            obj.y -= bias_2 + bias_1
        else:
            obj.rotate([0, 0, 1], math.radians(180))
            obj.x += bias_2
            obj.y -= bias_2 + bias_1

        if pipe.coordinates.start.y > pipe.coordinates.end.y:
            obj.y -= bias_2
        else:
            obj.y += bias_2

    obj.z += 120 + cum_z
    return obj


def rotate_otvod_45_upper_second(obj, pipe, cum_z, bias=90):
    bias_1, bias_2 = bias, 110
    if is_parallel_X(pipe.coordinates):
        obj.rotate([0, 0, 1], math.radians(180))
        obj.rotate([1, 0, 0], math.radians(-90))
        if pipe.coordinates.start.y > pipe.stuff.coordinates.y:
            pass
            obj.y -= bias_2
        else:
            obj.rotate([0, 0, 1], math.radians(180))
            obj.y += bias_2

        if pipe.coordinates.start.x > pipe.coordinates.end.x:
            obj.x += bias_1 - 5
        else:
            obj.x -= bias_1 - 5
    else:
        obj.rotate([0, 0, 1], math.radians(-90))
        obj.rotate([0, 1, 0], math.radians(90))
        if pipe.coordinates.start.x > pipe.stuff.coordinates.x:
            obj.x -= bias_2
            obj.y -= 3 * bias_1
        else:
            obj.rotate([0, 0, 1], math.radians(180))
            obj.x += bias_2
            obj.y -= 3 * bias_1

        if pipe.coordinates.start.y > pipe.coordinates.end.y:
            obj.y -= bias_2 - 5
        else:
            obj.y += bias_2 + 5

    obj.z += 120 + cum_z
    return obj


def shift_stuff_45(stuffs, pipe, bias=90):
    bias = bias
    if is_parallel_X(pipe.coordinates):
        if pipe.coordinates.start.y > pipe.stuff.coordinates.y:
            for stuff in stuffs:
                stuff.x += bias
        else:
            for stuff in stuffs:
                stuff.x -= bias
    else:
        if pipe.coordinates.start.x > pipe.stuff.coordinates.x:
            for stuff in stuffs:
                stuff.y -= bias
        else:
            for stuff in stuffs:
                stuff.y += bias
    return stuffs


def build_stuff_mesh_45(pipe: Pipe, material_graph: PipeGraph):
    meshes = []
    nodes = []
    is_troinik = False
    cum_z, bias_1 = 0, 50
    if pipe.is_end:
        fitting_name = "otvod_50x45"
        low_fitting = load_obj(FITTINGS[fitting_name])
        low_fitting = rotate_otvod_45_low(low_fitting, pipe, bias=40)
        # low_fitting = shift_rotate_low(low_fitting, pipe, 50)
        nodes.append(Node(FITTINGS[fitting_name]["name"], FITTINGS[fitting_name]["id"]))
    else:
        is_troinik = True
        cum_z = 30
        fitting_name = "troinik_50_50x45"
        low_fitting = load_obj(FITTINGS[fitting_name])
        low_fitting = rotate_troinik_toilet(low_fitting, pipe)
        nodes.append(
            Node(
                FITTINGS[fitting_name]["name"],
                FITTINGS[fitting_name]["id"],
                is_troinik=True,
            )
        )
    low_fitting.x += pipe.coordinates.start.x
    low_fitting.y += pipe.coordinates.start.y

    fitting_name = "otvod_50x45"
    otvod_lower_firts = load_obj(FITTINGS[fitting_name])
    otvod_lower_firts = rotate_otvod_45_lower_first(
        otvod_lower_firts, pipe, cum_z, bias=bias_1
    )
    nodes.append(
        Node(
            FITTINGS[fitting_name]["name"],
            FITTINGS[fitting_name]["id"],
            is_inside_troinik=True,
            is_end=False,
        )
    )
    otvod_lower_firts.x += pipe.coordinates.start.x
    otvod_lower_firts.y += pipe.coordinates.start.y

    fitting_name = "d50"
    straight_obj = load_obj(FITTINGS[fitting_name])
    straight_obj = center_pipe(straight_obj, "z")
    straight_obj_len = pipe.stuff.height
    straight_obj = cutout_pipe(straight_obj, pipe.stuff.height)
    straight_obj = shift_straight_pipe_45(straight_obj, pipe, cum_z + 30, bias=bias_1)
    straight_obj.x += pipe.coordinates.start.x
    straight_obj.y += pipe.coordinates.start.y
    straight_obj.z += pipe.stuff.height
    nodes.append(
        Node(
            FITTINGS[fitting_name]["name"],
            FITTINGS[fitting_name]["id"],
            length=straight_obj_len,
            is_inside_troinik=True,
        )
    )

    fitting_name = "otvod_50x45"
    otvod_upper_firts = load_obj(FITTINGS[fitting_name])
    otvod_upper_firts = rotate_otvod_45_upper_first(
        otvod_upper_firts, pipe, cum_z, bias=bias_1
    )
    nodes.append(
        Node(
            FITTINGS[fitting_name]["name"],
            FITTINGS[fitting_name]["id"],
            is_inside_troinik=True,
            is_end=False,
        )
    )
    otvod_upper_firts.x += pipe.coordinates.start.x
    otvod_upper_firts.y += pipe.coordinates.start.y
    otvod_upper_firts.z += pipe.stuff.height

    fitting_name = "otvod_50x45"
    otvod_upper_second = load_obj(FITTINGS[fitting_name])
    otvod_upper_second = rotate_otvod_45_upper_second(
        otvod_upper_second, pipe, cum_z, bias=bias_1+5
    )
    nodes.append(
        Node(
            FITTINGS[fitting_name]["name"],
            FITTINGS[fitting_name]["id"],
            is_inside_troinik=True,
            is_end=True,
        )
    )
    otvod_upper_second.x += pipe.coordinates.start.x
    otvod_upper_second.y += pipe.coordinates.start.y
    otvod_upper_second.z += pipe.stuff.height

    stuffs = [otvod_lower_firts, straight_obj, otvod_upper_firts, otvod_upper_second]
    stuffs = shift_stuff_45(stuffs, pipe, bias=30) if is_troinik else stuffs

    meshes = [low_fitting] + stuffs
    shift_stuff_after_reduction(meshes, pipe, diameter=50)
    shift_pipe_for_slope(meshes, pipe)
    material_graph.add_node(nodes, end=True)
    return meshes


def build_stuff_mesh_87(pipe: Pipe, material_graph: PipeGraph):
    meshes = []
    nodes = []
    if pipe.is_end:
        troinik = load_obj(FITTINGS["otvod_50x87"])
        troinik = rotate_otvod_low(troinik, pipe)
        troinik = shift_rotate_low(troinik, pipe, 50)
        nodes.append(
            Node(FITTINGS["otvod_50x87"]["name"], FITTINGS["otvod_50x87"]["id"])
        )
    else:
        troinik = load_obj(FITTINGS["troinik_50_50x87"])
        troinik = rotate_troinik_toilet(troinik, pipe)
        nodes.append(
            Node(
                FITTINGS["troinik_50_50x87"]["name"],
                FITTINGS["troinik_50_50x87"]["id"],
                is_troinik=True,
            )
        )
    troinik.x += pipe.coordinates.start.x
    troinik.y += pipe.coordinates.start.y
    bias = 100

    straight_obj = load_obj(FITTINGS["d50"])
    straight_obj = center_pipe(straight_obj, "z")
    straight_obj = cutout_pipe(straight_obj, pipe.stuff.height)
    straight_obj.x += pipe.coordinates.start.x
    straight_obj.y += pipe.coordinates.start.y
    straight_obj.z += pipe.stuff.height
    nodes.append(
        Node(FITTINGS["d50"]["name"], FITTINGS["d50"]["id"], is_inside_troinik=True)
    )

    otvod = load_obj(FITTINGS["otvod_50x87"])
    otvod = rotate_otvod(otvod, pipe)
    shift_otvod(otvod, pipe, 50)
    nodes.append(
        Node(
            FITTINGS["otvod_50x87"]["name"],
            FITTINGS["d50"]["id"],
            is_inside_troinik=True,
            is_end=True,
        )
    )
    otvod.x += pipe.coordinates.start.x
    # otvod.x -= 80
    otvod.y += pipe.coordinates.start.y
    otvod.z += pipe.stuff.height

    # if pipe.coordinates.start.y < pipe.coordinates.end.y:
    #     troinik.y -= bias
    #     straight_obj.y -= bias - 30
    #     otvod.y -= bias - 30
    # if pipe.coordinates.start.x < pipe.coordinates.end.x:
    #     troinik.x -= bias
    #     straight_obj.x -= bias - 30
    #     otvod.x -= bias - 30

    meshes = [straight_obj, troinik, otvod]
    material_graph.add_node(nodes, end=True)
    return meshes


def rotate_otvod_link_knee(obj, pipe, riser_projections, diameter=110):
    bias_1 = 160 if diameter == 110 else 110
    bias_2 = 37 if diameter == 110 else 0
    bias_3 = 55 if diameter == 110 else 55
    if is_parallel_X(pipe.coordinates):
        if pipe.coordinates.end.y > riser_projections.y:  # pipe above riser
            if pipe.coordinates.start.x < pipe.coordinates.end.x:  # right
                obj.rotate([0, 0, 1], math.radians(180))
                obj.rotate([0, 1, 0], math.radians(90))
                obj.y += bias_2
                obj.x -= bias_1 - 47
            else:
                obj.rotate([0, 0, 1], math.radians(180))
                obj.rotate([0, 1, 0], math.radians(-90))
                obj.x += bias_1 - 37
                obj.y += bias_2
        else:
            if pipe.coordinates.start.x < pipe.coordinates.end.x:  # right
                obj.rotate([0, 1, 0], math.radians(90))
                obj.x -= bias_3
            else:
                obj.rotate([0, 1, 0], math.radians(-90))
                obj.x += bias_1 - 40 if diameter == 110 else bias_1
                obj.y += bias_1
                obj.y -= bias_1 if diameter == 50 else 0
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
                # obj.y -= 160
                obj.y -= 120
            else:
                obj.rotate([0, 0, 1], math.radians(-90))
                obj.rotate([1, 0, 0], math.radians(90))
    return obj


def build_knee_fitting(pipe, riser_projections, material_graph: PipeGraph):
    fitting_meta = (
        FITTINGS["otvod_110x87"] if pipe.is_toilet else FITTINGS["otvod_50x87"]
    )
    diameter = 110 if pipe.is_toilet else 50
    obj = load_obj(fitting_meta)
    obj = rotate_otvod_link_knee(obj, pipe, riser_projections, diameter)
    obj.x += pipe.coordinates.end.x
    obj.y += pipe.coordinates.end.y
    shift_stuff_after_reduction(obj, pipe, diameter)
    shift_knee_for_slope(obj, pipe)
    node = Node(fitting_meta["name"], fitting_meta["id"])
    material_graph.add_node(node)
    return [obj]


def rotate_otvod_link_knee_45(obj, pipe, riser_projections, first=True):
    bias_1 = 40
    bias_2 = 40
    bias_3 = 100
    bias_4 = 110
    if is_parallel_X(pipe.coordinates):
        if pipe.coordinates.end.y > riser_projections.y:  # pipe above riser
            if pipe.coordinates.start.x < pipe.coordinates.end.x:  # right
                obj.rotate([0, 0, 1], math.radians(180))
                obj.rotate([0, 1, 0], math.radians(90))
                if not first:
                    obj.rotate([0, 0, 1], math.radians(45))
                    obj.y -= 0
                    obj.x += 70
                obj.x -= 90
            else:
                obj.rotate([0, 0, 1], math.radians(180))
                obj.rotate([0, 1, 0], math.radians(-90))
                if not first:
                    obj.rotate([0, 0, 1], math.radians(-45))
                    obj.y -= 20
                    obj.x -= bias_2
                else:
                    obj.y += 0
                    obj.x += 40
                obj.x += bias_4
        else:
            if pipe.coordinates.start.x < pipe.coordinates.end.x:  # right
                obj.rotate([0, 1, 0], math.radians(90))
                if not first:
                    obj.rotate([0, 0, 1], math.radians(-45))
                    obj.y += 20
                    obj.x -= 20
                else:
                    obj.x -= 100
            else:
                obj.rotate([0, 1, 0], math.radians(-90))
                if not first:
                    obj.rotate([0, 0, 1], math.radians(45))
                    obj.y += 20
                    obj.x -= bias_2
                else:
                    obj.y += 0
                    obj.x += 40
                obj.x += bias_4
    else:
        # CHECKED
        if pipe.coordinates.end.x < riser_projections.x:  # pipe -> riser
            if pipe.coordinates.start.y < pipe.coordinates.end.y:  # up
                obj.rotate([0, 0, 1], math.radians(90))
                obj.rotate([1, 0, 0], math.radians(-90))
                if first:
                    obj.rotate([0, 0, 1], math.radians(45))
                    obj.y -= bias_1
                else:
                    obj.y -= bias_3
                obj.y -= bias_1
            else:
                obj.rotate([0, 0, 1], math.radians(90))
                obj.rotate([1, 0, 0], math.radians(90))
                if not first:
                    obj.rotate([0, 0, 1], math.radians(-45))
                    obj.x += 10
                    obj.y += 5
                else:
                    obj.y += 80
        else:  # riser -> pipe
            # CHECKED
            if pipe.coordinates.start.y < pipe.coordinates.end.y:  # up
                obj.rotate([1, 0, 0], math.radians(-90))
                obj.rotate([0, 1, 0], math.radians(90))
                if first:
                    obj.rotate([0, 0, 1], math.radians(-45))
                    obj.y -= bias_1
                else:
                    obj.y -= bias_3
                obj.y -= bias_2
            else:
                obj.rotate([0, 0, 1], math.radians(-90))
                obj.rotate([1, 0, 0], math.radians(90))
                if first:
                    obj.rotate([0, 0, 1], math.radians(45))
                    obj.x -= 15
                    obj.y += 5
                else:
                    obj.y += 80
    return obj


def build_knee_fitting_45(
    pipe: Pipe, riser_projections: Point, material_graph: PipeGraph
):
    nodes = []
    fitting_meta = FITTINGS["otvod_50x45"]
    obj_first = load_obj(fitting_meta)
    obj_first = rotate_otvod_link_knee_45(
        obj_first, pipe, riser_projections, first=True
    )
    obj_second = load_obj(fitting_meta)
    obj_second = rotate_otvod_link_knee_45(
        obj_second, pipe, riser_projections, first=False
    )
    obj_first.x += pipe.coordinates.end.x
    obj_first.y += pipe.coordinates.end.y
    obj_second.x += pipe.coordinates.end.x
    obj_second.y += pipe.coordinates.end.y
    stuffs = [obj_first, obj_second]
    shift_stuff_after_reduction(stuffs, pipe, diameter=50)
    shift_knee_for_slope(stuffs, pipe)
    nodes = [Node(fitting_meta["name"], fitting_meta["id"])] * 2
    material_graph.add_node(nodes)
    return stuffs


def build_riser(riser_coordinates, riser_projections, walls):
    fitting_meta = FITTINGS["troinik_110_110x87"]
    obj = load_obj(fitting_meta)
    obj = rotate_riser(obj, riser_coordinates, riser_projections, walls)
    obj.x += riser_coordinates.x
    obj.y += riser_coordinates.y
    obj.z += 60
    node = Node(fitting_meta["name"], fitting_meta["id"], is_start=True)
    return obj, node


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
    return obj


def build_riser_otvod(riser_coordinates, riser_projections, walls, both_side=True):
    toilet_coordinates = get_toilet_coordinates_form_wall(walls)
    pipe = "right"
    # fitting_meta = FITTINGS["otvod_110x87"]
    fitting_meta = (
        FITTINGS["otvod_110_50_87_back"] if both_side else FITTINGS["otvod_110x87"]
    )
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
        if toilet_coordinates.x > riser_projections.x:  # toilet on right
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
            y_bias = 0
            x_bias = -60
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
            y_bias = 40
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
            x_bias = 0
    # print(pipe_)
    obj = rotate_otvod_link_knee(obj, pipe, riser_projections, 110)
    obj.x += riser_projections.x
    obj.y += riser_projections.y
    obj.y += y_bias
    obj.x += x_bias
    node = Node(fitting_meta["name"], fitting_meta["id"])
    return obj, node


def build_riser_to_otvod_pipe(riser_coordinates, riser_projections, treshold=400):
    bias1 = 0
    bias2 = 0
    if (
        riser_coordinates.y <= riser_projections.y - treshold
    ):  # proj higher more than 200
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
        pipe = Pipe(
            Segment(
                start=Point(riser_projections.x, riser_projections.y),
                end=Point(riser_projections.x, riser_coordinates.y),
            )
        )
        bias2 = +50

    elif (
        riser_coordinates.x - treshold >= riser_projections.x
    ):  # proj left more than 200
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
        pipe = Pipe(
            Segment(
                start=Point(riser_coordinates.x, riser_projections.y),
                end=Point(riser_projections.x, riser_coordinates.y),
            )
        )
        bias1 = 60
    else:
        return None, None
    obj_meta = FITTINGS["d110"]
    obj, node = build_pipe_mesh(obj_meta, pipe, "87", 30)
    obj.x += bias1
    obj.y += bias2
    node = Node(
        obj_meta["name"],
        obj_meta["id"],
        l1_distance(pipe.coordinates.start, pipe.coordinates.end),
    )
    return obj, node


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
        return None, None
    meta_obj = FITTINGS["d110"]
    obj, node = build_pipe_mesh(meta_obj, pipe)
    obj.x += bias_x
    obj.y += bias_y
    return obj, node


def build_pipe_arrows(pipe: Pipe, start_height=100):
    length_arrow = 200
    for x_arr_start, y_arr_start in [
        (pipe.coordinates.start.x, pipe.coordinates.start.y),
        (pipe.coordinates.end.x, pipe.coordinates.end.y),
    ]:
        x = np.array([length_arrow + x_arr_start, y_arr_start, start_height])
        y = np.array([x_arr_start, length_arrow + y_arr_start, start_height])
        z = np.array([x_arr_start, y_arr_start, length_arrow + start_height])
        vpl.arrow([x_arr_start, y_arr_start, start_height], x, color="white")
        vpl.arrow([x_arr_start, y_arr_start, start_height], y, color="white")
        vpl.arrow([x_arr_start, y_arr_start, start_height], z, color="white")


def draw_bath_arrows(walls: Wall, start_height=100):
    x_max, y_min = [], []
    for wall in walls:
        x_max.extend([wall.coordinates.start.x, wall.coordinates.end.x])
        y_min.extend([wall.coordinates.start.y, wall.coordinates.end.y])
    x_max = np.max(x_max)
    y_min = np.min(y_min)
    length_arrow = 300
    x_max += 200
    y_min -= 200
    x = np.array([length_arrow + x_max, y_min, start_height])
    y = np.array([x_max, length_arrow + y_min, start_height])
    z = np.array([x_max, y_min, length_arrow + start_height])
    vpl.arrow([x_max, y_min, start_height], x, color="black")
    vpl.arrow([x_max, y_min, start_height], y, color="black")
    vpl.arrow([x_max, y_min, start_height], z, color="black")

    vpl.text3d("X", x, scale=60, color="k")
    vpl.text3d("Y", y, scale=60, color="k")
    vpl.text3d("Z", z, scale=60, color="k")
