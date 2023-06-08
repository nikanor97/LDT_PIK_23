import math
from src.trace_builder.geometry import is_parallel_X, is_parallel_Y
from src.trace_builder.manipulate_3d import rotate_troinik_toilet, load_obj, cutout_pipe, l1_distance, center_pipe, rotate_otvod_45_low, shift_straight_pipe_45
from src.trace_builder.mesh_3d.common import rotate_otvod_87_upper, shift_stuff
from src.trace_builder.models import Pipe
from src.trace_builder.graph_models import PipeGraph, Node
from src.trace_builder.constants import FITTINGS


def rotate_otvod_30_lower_first(obj, pipe, cum_z, bias=90):
    bias_1, bias_z = bias, 110 + cum_z
    if is_parallel_X(pipe.coordinates):
        obj.rotate([0, 0, 1], math.radians(-90))
        obj.rotate([0, 1, 0], math.radians(-15))
        if pipe.coordinates.start.x > pipe.coordinates.end.x:  # stream to left
            obj.x += bias_1
            obj.z += bias_z
            pass
        else:  # stream to right
            obj.rotate([0, 0, 1], math.radians(180))
            obj.x -= bias_1
            obj.z += bias_z
    else:
        obj.rotate([1, 0, 0], math.radians(-15))
        if pipe.coordinates.start.y > pipe.coordinates.end.y:  # stream to down
            obj.rotate([0, 0, 1], math.radians(180))
            obj.z += bias_z
            obj.y += bias_1
        else:  # stream to up
            obj.y -= bias_1
            obj.z += bias_z
    return obj

def rotate_otvod_15_lower_second(obj, pipe, cum_z, bias=90):
    bias_1, bias_z = bias, 170 + cum_z
    if is_parallel_X(pipe.coordinates):
        obj.rotate([0, 0, 1], math.radians(-90))
        if pipe.coordinates.start.x > pipe.coordinates.end.x:  # stream to left
            obj.x += bias_1
            pass
        else:  # stream to right
            obj.rotate([0, 0, 1], math.radians(180))
            obj.x -= bias_1
    else:
        if pipe.coordinates.start.y > pipe.coordinates.end.y:  # stream to down
            obj.rotate([0, 0, 1], math.radians(180))
            obj.y += bias_1
        else:  # stream to up
            obj.y -= bias_1
    obj.z += bias_z
    return obj

def build_stuff_mesh_30_15(pipe: Pipe, material_graph: PipeGraph):
    meshes = []
    nodes = []
    is_troinik = False
    cum_z, bias_1 = 0, 65
    if pipe.is_end:
        fitting_name = "otvod_50x45"
        low_fitting = load_obj(FITTINGS[fitting_name])
        low_fitting = rotate_otvod_45_low(low_fitting, pipe, bias=40)
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

    fitting_name = "otvod_50x30"
    otvod_lower_firts = load_obj(FITTINGS[fitting_name])
    otvod_lower_firts = rotate_otvod_30_lower_first(otvod_lower_firts, pipe, cum_z, bias=bias_1)
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

    fitting_name = "otvod_50x15"
    otvod_lower_second = load_obj(FITTINGS[fitting_name])
    otvod_lower_second = rotate_otvod_15_lower_second(otvod_lower_second, pipe, cum_z, bias=bias_1)
    nodes.append(
        Node(
            FITTINGS[fitting_name]["name"],
            FITTINGS[fitting_name]["id"],
            is_inside_troinik=True,
            is_end=False,
        )
    )
    otvod_lower_second.x += pipe.coordinates.start.x
    otvod_lower_second.y += pipe.coordinates.start.y

    straight_obj = None
    if pipe.stuff.height > 200:
        fitting_name = "d50"
        straight_obj = load_obj(FITTINGS[fitting_name])
        straight_obj = center_pipe(straight_obj, "z")
        straight_obj = cutout_pipe(straight_obj, pipe.stuff.height - 40)
        straight_obj = shift_straight_pipe_45(straight_obj, pipe, cum_z+30, bias=bias_1)
        straight_obj.x += pipe.coordinates.start.x
        straight_obj.y += pipe.coordinates.start.y
        straight_obj.z += pipe.stuff.height
        nodes.append(
            Node(FITTINGS[fitting_name]["name"], FITTINGS[fitting_name]["id"], length=l1_distance(pipe.coordinates.start, pipe.coordinates.end), is_inside_troinik=True)
        )

    fitting_name = "otvod_50x87"
    otvod_upper_firts = load_obj(FITTINGS[fitting_name])
    otvod_upper_firts = rotate_otvod_87_upper(otvod_upper_firts, pipe, 200+cum_z, bias_1, 130)
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
    if pipe.stuff.height > 200:
        otvod_upper_firts.z += pipe.stuff.height - 100

    stuffs = [otvod_lower_firts, otvod_lower_second, otvod_upper_firts]
    if straight_obj:
        stuffs.append(straight_obj)
    stuffs = shift_stuff(stuffs, pipe, bias=30) if is_troinik else stuffs

    meshes = [low_fitting] + stuffs
    material_graph.add_node(nodes, end=True)
    return meshes
