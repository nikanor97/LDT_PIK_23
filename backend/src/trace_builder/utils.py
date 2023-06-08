import json

from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib.pyplot as plt

from src.trace_builder.coordinate_converter import (coordinate2point,
                                                    coordinates2segment,
                                                    coordinates2segments,
                                                    point2coordinate,
                                                    segment2coordinates,
                                                    segments2coordinates)
from src.trace_builder.models import Stuff
import pandas as pd


def save_data(
    stuffs,
    walls,
    max_riser_height,
    optimal_segment,
    riser_coordinates,
    riser_projection,
):
    for stuff in stuffs.keys():
        stuffs[stuff]["coordinates"] = point2coordinate(stuffs[stuff]["coordinates"])
        stuffs[stuff]["projection"] = point2coordinate(stuffs[stuff]["projection"])
        stuffs[stuff]["segment"] = segment2coordinates(stuffs[stuff]["segment"])

    walls = segments2coordinates(walls)
    result = {
        "max_riser_height": max_riser_height,
        "stuff": stuffs,
        "walls": walls,
        "optimal_wall": optimal_segment,
        "riser_coordinates": point2coordinate(riser_coordinates),
        "riser_projection": point2coordinate(riser_projection),
    }
    with open("geometry.json", "w") as f:
        json.dump(result, f)


def load_data(path):
    with open(path, "r") as f:
        data = json.load(f)
    max_riser_height = data["max_riser_height"]
    optimal_segment = data["optimal_wall"]
    walls = coordinates2segments(data["walls"])
    riser_projection = coordinate2point(data["riser_projection"])
    riser_coordinates = coordinate2point(data["riser_coordinates"])
    for stuff in data["stuff"].keys():
        data["stuff"][stuff]["l1_projection"] = data["stuff"][stuff]["l1_projection"]
        data["stuff"][stuff]["riser_l1_distance"] = data["stuff"][stuff][
            "riser_l1_distance"
        ]
        data["stuff"][stuff]["height"] = data["stuff"][stuff]["height"]
        data["stuff"][stuff]["projection"] = coordinate2point(
            data["stuff"][stuff]["projection"]
        )
        data["stuff"][stuff]["segment"] = coordinates2segment(
            data["stuff"][stuff]["segment"]
        )
        data["stuff"][stuff]["coordinates"] = coordinate2point(
            data["stuff"][stuff]["coordinates"]
        )

    stuff = data["stuff"]
    return (
        stuff,
        walls,
        optimal_segment,
        max_riser_height,
        riser_coordinates,
        riser_projection,
    )


def dict2stuff(stuffs):
    stuffs_classes = []
    for stuff, info in stuffs.items():
        stuff_object = Stuff(
            stuff,
            info["coordinates"],
            info["projection"],
            info["segment"],
            info["l1_projection"],
            info["riser_l1_distance"],
            info["height"],
        )
        stuffs_classes.append(stuff_object)
    return stuffs_classes


def convert_dxf2img(doc, img_name, img_res=1440):
    msp = doc.modelspace()
    # Recommended: audit & repair DXF document before rendering
    auditor = doc.audit()
    # The auditor.errors attribute stores severe errors,
    # which *may* raise exceptions when rendering.
    if len(auditor.errors) != 0:
        raise Exception("The DXF document is damaged and can't be converted!")
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    ctx = RenderContext(doc)
    ctx.set_current_layout(msp)
    out = MatplotlibBackend(ax)
    Frontend(ctx, out).draw_layout(msp, finalize=True)
    fig.savefig(img_name, dpi=img_res)

def fittings_count(graph):
    fitting_count = 0
    materials = graph["Материал"].values
    for material in materials:
        if material not in [501, 500]:
            fitting_count += 1
    return fitting_count

def calculate_statistic(graph: pd.DataFrame):
    fitting_counts = fittings_count(graph)
    length = graph[(graph["Материал"] == 500) | (graph["Материал"] == 501)]["Длина"].values.sum()
    return fitting_counts, length
