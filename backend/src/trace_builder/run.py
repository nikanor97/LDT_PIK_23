import ezdxf


from coordinate_converter import (
    coordinate2point,
    coordinates2segment,
    coordinates2segments,
    point2coordinate,
    segment2coordinates,
    segments2coordinates,
)
from projections import (
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
    plot_projcetions,
    distance_from_riser_to_stuff,
    calculate_max_riser_height,
    clear_sutff_duplicate,
    save_data,
)

from path import (
    detect_walls_with_stuff,
    build_path_from_riser_wall_to_sutff_wall,
    build_path,
)
from merge_segments import merge_segments
from geometry import (
    is_dot_inside_segment,
    l1_distance,
    l2_distance,
    detect_wall_with_door,
)
from utils import load_data, save_data, dict2stuff
from time import time
import pandas as pd
import os


def run_algo(dxf_path: str, heighs: dict()):
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

    dir_name = "outgoing"
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    timestam = int(time())
    scrennshot_name = f"{dir_name}/{timestam}.png"
    mesh = build_path(walls, riser_projections, scrennshot_name)
    mesh.save(f"{scrennshot_name}.stl")
    pd.DataFrame({"Граф": ["A-1", "1-2"], "Материал": [101, 102]}).to_csv(
        f"{dir_name}/graph.csv"
    )
    output_dir = os.getcwd() + "/" + dir_name
    return output_dir


if __name__ == "__main__":
    hieghts = {
        "SND_2D_Раковина1 - 550х400-16253994-Битца 8_ТИПИЗАЦИЯ": 100,
        "SEQ_2D_Стиральная машина - 600x600-V57-Битца 8_ТИПИЗАЦИЯ": 200,
        "АИ_2D_Ванна 1685х700 - 2D_Ванна 1700х700-16267569-Битца 8_ТИПИЗАЦИЯ": 300,
        "АИ_2D_Кран настенный для ванны с душем1 - 2D_Кран настенный для ванны с душем 2-16267571-Битца 8_ТИПИЗАЦИЯ": 300,
        "SND_2D_Эскиз_Мойка_Кухня - SND_2D_Эскиз_Мойка_Кухня-16115635-Битца 8_ТИПИЗАЦИЯ": 150,
        "Унитаз_3D_С бачком_Рен - 2D_Унитаз_Бачок-V58-Битца 8_ТИПИЗАЦИЯ": 100,
    }
    run_algo("data/СТМ8-1П-Б-2.dxf", hieghts)
