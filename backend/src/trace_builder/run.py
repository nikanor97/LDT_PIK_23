import os
from pathlib import Path
from random import randint
from time import time

import ezdxf
import settings
from src.db.projects.models import SewerVariantBase
from src.trace_builder.coordinate_converter import coordinates2segments
from src.trace_builder.merge_segments import merge_segments
from src.trace_builder.path import (
    build_path,
    build_path_from_riser_wall_to_sutff_wall,
    detect_walls_with_stuff,
)
from src.trace_builder.projections import (
    build_riser_projections,
    calculate_max_riser_height,
    check_wall_coordinates,
    clear_sutff_duplicate,
    distance_from_riser_to_stuff,
    entities_with_coordinates,
    extract_rectange_points,
    extract_riser_coordinates,
    filter_wall_by_distance,
    find_middle_points,
    find_optimal_riser_projection,
    find_rect_corners,
    get_stuff_projcetions,
    get_top3_segmets,
    projection,
)
from src.trace_builder.utils import dict2stuff


def run_algo(
    dxf_path: str, heighs: dict, save_path: Path, file_suffix: str = ""
) -> list[SewerVariantBase]:
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
    output_files = f"{save_path}/{timestam}{file_suffix}"
    mesh, material_graph = build_path(
        walls, riser_projections, riser_coordinates, f"{output_files}.png"
    )
    mesh.save(f"{output_files}.stl")
    material_graph.to_csv(f"{output_files}.csv", index=True)

    sewer_variant = SewerVariantBase(
        excel_source_url=f"{output_files}.csv",
        stl_source_url=f"{output_files}.stl",
        png_source_url=f"{output_files}.png",
        variant_num=1,
    )

    return [sewer_variant]


if __name__ == "__main__":
    hieghts = {
        "SND_2D_Раковина1 - 550х400-16253994-Битца 8_ТИПИЗАЦИЯ": 100,
        "SEQ_2D_Стиральная машина - 600x600-V57-Битца 8_ТИПИЗАЦИЯ": 200,
        "АИ_2D_Ванна 1685х700 - 2D_Ванна 1700х700-16267569-Битца 8_ТИПИЗАЦИЯ": 300,
        "АИ_2D_Кран настенный для ванны с душем1 - 2D_Кран настенный для ванны с душем 2-16267571-Битца 8_ТИПИЗАЦИЯ": 300,
        "SND_2D_Эскиз_Мойка_Кухня - SND_2D_Эскиз_Мойка_Кухня-16115635-Битца 8_ТИПИЗАЦИЯ": 150,
        "Унитаз_3D_С бачком_Рен - 2D_Унитаз_Бачок-V58-Битца 8_ТИПИЗАЦИЯ": 100,
    }
    files = [
        "СТМ8-1П-А-1.dxf",
        # "СТМ8-1П-Б-2.dxf",
        # "СТМ8-2Л-А-1.dxf",
        # "СТМ8-2Л-Б-1.dxf",
        # "СТМ8-4П-А-1.dxf",
    ]
    for file in files:
        run_algo(
            settings.BASE_DIR / "data_samples" / "setup_examples" / file,
            hieghts,
            settings.MEDIA_DIR / "builder_outputs",
        )

# "СТМ8-1П-А-1.dxf"
# "СТМ8-1П-Б-2.dxf"
# "СТМ8-2Л-А-1.dxf"
# "СТМ8-2Л-Б-1.dxf"
# "СТМ8-4П-А-1.dxf"
