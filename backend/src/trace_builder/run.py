import os
from pathlib import Path
from time import time

import settings
from src.trace_builder.path import build_path
from src.trace_builder.projections import process_file_geometry
from src.db.projects.models import SewerVariantBase


def run_algo(dxf_path: str, heighs: dict, save_path: Path, file_suffix: str = "") -> list[SewerVariantBase]:

    walls, riser_projections, riser_coordinates, max_riser_height = process_file_geometry(dxf_path, heighs)

    if not os.path.exists(save_path):
        os.makedirs(save_path)
    timestamp = int(time())
    output_files = f"{save_path}/{timestamp}{file_suffix}"
    mesh, material_graph = build_path(
        walls,
        riser_projections,
        riser_coordinates,
        f"{output_files}.png",
        scenario="30_15",
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
        "СТМ8-1П-Б-2.dxf",
        "СТМ8-2Л-А-1.dxf",
        "СТМ8-2Л-Б-1.dxf",
        "СТМ8-4П-А-1.dxf",
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
