import math
from typing import List, Any
from src.trace_builder.geometry import is_parallel_X
from src.trace_builder.models import Pipe
from src.trace_builder.constants import REDUCTION_SHIFT

def shift_stuff(stuffs, pipe, bias=90):
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

def shift_stuff_after_reduction(stuffs: List[Any], pipe: Pipe, diameter = 110):
    if pipe.after_reduction and diameter != 110:
        if isinstance(stuffs, list):
            for stuff in stuffs:
                stuff.z -= REDUCTION_SHIFT
        else:
            stuffs.z -= REDUCTION_SHIFT
    return stuffs


def rotate_otvod_87_upper(obj, pipe, cum_z, bias=90, bias_3=90):
    bias_1, bias_2 = bias, 80
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
            obj.x += bias_1
        else:
            obj.x -= bias_1
    else:
        obj.rotate([0, 0, 1], math.radians(-90))
        obj.rotate([0, 1, 0], math.radians(90))
        if pipe.coordinates.start.x > pipe.stuff.coordinates.x:
            obj.x -= bias_2
            obj.y -= bias_3
        else:
            obj.rotate([0, 0, 1], math.radians(180))
            obj.x += bias_2
            obj.y -= bias_3

        if pipe.coordinates.start.y > pipe.coordinates.end.y:
            obj.y -= bias_2
        else:
            obj.y += bias_2

    obj.z += cum_z
    return obj