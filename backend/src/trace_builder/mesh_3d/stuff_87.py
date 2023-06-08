import math
from src.trace_builder.geometry import is_parallel_X, is_parallel_Y
from src.trace_builder.manipulate_3d import rotate_troinik_toilet, load_obj, cutout_pipe, l1_distance, center_pipe, rotate_otvod_45_low, shift_straight_pipe_45
from src.trace_builder.mesh_3d.common import rotate_otvod_87_upper, shift_stuff
from src.trace_builder.models import Pipe
from src.trace_builder.graph_models import PipeGraph, Node
from src.trace_builder.constants import FITTINGS



def rotate_otvod_87_low(obj, pipe, cum_z, bias=90):
    bias_1, bias_z = bias, 80 + cum_z
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
        if pipe.coordinates.start.y > pipe.coordinates.end.y:  # stream to down
            obj.rotate([0, 0, 1], math.radians(180))
            obj.z += bias_z
            obj.y += bias_1
        else:  # stream to up
            obj.y -= bias_1
            obj.z += bias_z
    return obj


def build_stuff_mesh_87(pipe: Pipe, material_graph: PipeGraph):
    meshes = []
    nodes = []
    cum_z, bias_1 = 0, 10
    is_troinik = False
    if pipe.is_end:
        fitting_name = "otvod_50x87"
        troinik = load_obj(FITTINGS[fitting_name])
        troinik = rotate_otvod_87_low(troinik, pipe, cum_z, 10)
        nodes.append(
            Node(FITTINGS[fitting_name]["name"], FITTINGS[fitting_name]["id"])
        )
    else:
        is_troinik = True
        fitting_name = "troinik_50_50x87"
        troinik = load_obj(FITTINGS[fitting_name])
        troinik = rotate_troinik_toilet(troinik, pipe)
        nodes.append(
            Node(
                FITTINGS[fitting_name]["name"],
                FITTINGS[fitting_name]["id"],
                is_troinik=True,
            )
        )
    troinik.x += pipe.coordinates.start.x
    troinik.y += pipe.coordinates.start.y

    cum_z = 0
    fitting_name = "d50"
    straight_obj = load_obj(FITTINGS[fitting_name])
    straight_obj = center_pipe(straight_obj, "z")
    straight_obj_len = pipe.stuff.height - 10
    straight_obj = cutout_pipe(straight_obj, straight_obj_len)
    straight_obj = shift_straight_pipe_45(straight_obj, pipe, cum_z, bias=bias_1)
    straight_obj.x += pipe.coordinates.start.x
    straight_obj.y += pipe.coordinates.start.y
    straight_obj.z += pipe.stuff.height
    nodes.append(
        Node(FITTINGS[fitting_name]["name"], FITTINGS[fitting_name]["id"], is_inside_troinik=True, length=straight_obj_len)
    )

    fitting_name = "otvod_50x87"
    otvod_upper = load_obj(FITTINGS[fitting_name])
    up_otovd =  cum_z + pipe.stuff.height + 60
    otvod_upper = rotate_otvod_87_upper(otvod_upper, pipe, up_otovd, bias_1, 90)
    nodes.append(
        Node(
            FITTINGS[fitting_name]["name"],
            FITTINGS[fitting_name]["id"],
            is_inside_troinik=True,
            is_end=True,
        )
    )
    otvod_upper.x += pipe.coordinates.start.x
    otvod_upper.y += pipe.coordinates.start.y


    stuffs = [straight_obj, otvod_upper]
    stuffs = shift_stuff(stuffs, pipe, bias=40) if is_troinik else stuffs

    meshes = stuffs + [troinik]
    material_graph.add_node(nodes, end=True)
    return meshes
