from pathlib import Path

import ezdxf

import settings
from src.trace_builder.coordinate_converter import (
    coordinates2segments,
)
from src.trace_builder.projections import (
    extract_riser_coordinates,
    extract_rectange_points,
    find_rect_corners,
    find_middle_points,
    entities_with_coordinates,
    filter_wall_by_distance,
    get_stuff_projcetions,
    build_riser_projections,
    find_optimal_riser_projection,
    projection,
    distance_from_riser_to_stuff,
    calculate_max_riser_height,
    clear_sutff_duplicate,
)

from src.trace_builder.path import (
    detect_walls_with_stuff,
    build_path_from_riser_wall_to_sutff_wall,
    build_path,
)
from src.trace_builder.merge_segments import merge_segments
from src.trace_builder.geometry import (
    detect_wall_with_door,
)
from src.trace_builder.utils import dict2stuff
from time import time
import pandas as pd
import os


def run_algo(dxf_path: str, heighs: dict, save_path: Path):
    doc = ezdxf.readfile(dxf_path)
    modelspace = doc.modelspace()
    msp = modelspace

    riser_coordinates = extract_riser_coordinates(doc)
    coordinates = extract_rectange_points(msp)
    rectangle_coordinates = [
        find_rect_corners(coordinate, 0.5) for coordinate in coordinates
    ]
    mid_points = [
        find_middle_points(coordinate) for coordinate in rectangle_coordinates
    ]
    mid_points_ = coordinates2segments(mid_points)

    # print(mid_points)
    # line_coeffs = [lin_equ(*points) for points in mid_points]

    stuffs = entities_with_coordinates(msp)

    mid_points_merged = merge_segments(mid_points_, 100)
    mid_points_merged = merge_segments(mid_points_merged, 100)
    mid_point_filtered = [
        segment
        for segment in mid_points_merged
        if filter_wall_by_distance(segment, 100)
    ]

    segments_with_wall_flag = detect_wall_with_door(mid_point_filtered)

    stuff_projections = get_stuff_projcetions(stuffs, segments_with_wall_flag, False)

    riser_projection_distances = build_riser_projections(
        riser_coordinates, mid_point_filtered
    )

    optimal_segment = find_optimal_riser_projection(
        riser_projection_distances, stuff_projections
    )
    riser_projection = projection(
        riser_coordinates, mid_point_filtered[optimal_segment]
    )

    distance_from_riser_to_stuff(riser_projection, stuff_projections)

    for key in stuff_projections.keys():
        stuff_projections[key]["height"] = heighs[key]

    max_riser_height = calculate_max_riser_height(stuff_projections)
    # %%
    clear_sutff_duplicate(stuff_projections)
    stuffs = stuff_projections
    walls_segments = mid_point_filtered
    riser_projections = riser_projection
    stuffs_objects = dict2stuff(stuffs)

    walls = detect_walls_with_stuff(stuffs_objects, walls_segments, riser_projections)
    walls = sorted(walls, key=lambda x: x.length, reverse=True)[:3]
    walls = build_path_from_riser_wall_to_sutff_wall(walls)

    # dir_name = "outgoing"
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    timestam = int(time())
    output_files = f"{save_path}/{timestam}"
    mesh = build_path(walls, riser_projections, riser_coordinates, f"{output_files}.png")
    mesh.save(f"{output_files}.stl")
    pd.DataFrame({"Граф": ["A-1", "1-2"], "Материал": [101, 102]}).to_csv(
        f"{output_files}.csv"
    )
    # output_dir = os.getcwd() + "/" + str(save_path)
    # return output_dir
    return f"{output_files}.csv", output_files, f"{output_files}.stl"


if __name__ == "__main__":
    hieghts = {
        "SND_2D_Раковина1 - 550х400-16253994-Битца 8_ТИПИЗАЦИЯ": 100,
        "SEQ_2D_Стиральная машина - 600x600-V57-Битца 8_ТИПИЗАЦИЯ": 200,
        "АИ_2D_Ванна 1685х700 - 2D_Ванна 1700х700-16267569-Битца 8_ТИПИЗАЦИЯ": 300,
        "АИ_2D_Кран настенный для ванны с душем1 - 2D_Кран настенный для ванны с душем 2-16267571-Битца 8_ТИПИЗАЦИЯ": 300,
        "SND_2D_Эскиз_Мойка_Кухня - SND_2D_Эскиз_Мойка_Кухня-16115635-Битца 8_ТИПИЗАЦИЯ": 150,
        "Унитаз_3D_С бачком_Рен - 2D_Унитаз_Бачок-V58-Битца 8_ТИПИЗАЦИЯ": 100,
    }
    run_algo(
        settings.BASE_DIR / "data_samples" / "setup_examples" / "СТМ8-1П-Б-2.dxf",
        hieghts,
        settings.MEDIA_DIR / "builder_outputs",
    )

# %%
