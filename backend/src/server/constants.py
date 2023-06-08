from typing import Optional

from pydantic import BaseModel


class FittingCreate(BaseModel):
    name: str
    groupname: str
    image_path: str
    material_id: Optional[str]


fittings_config = [
    FittingCreate(
        name="Ревизия 110", groupname="Ревизия", image_path="fittings/Group 1.png"
    ),
    FittingCreate(
        name="Тройник 50х50х45",
        groupname="Тройники",
        image_path="fittings/Group 51.png",
        material_id="106",
    ),
    FittingCreate(
        name="Тройник 50х50х87",
        groupname="Тройники",
        image_path="fittings/Group 52.png",
        material_id="105",
    ),
    FittingCreate(
        name="Тройник 110х50х87",
        groupname="Тройники",
        image_path="fittings/Group 53.png",
        material_id="102",
    ),
    FittingCreate(
        name="Тройник 110х110х87",
        groupname="Тройники",
        image_path="fittings/Group 57.png",
        material_id="101",
    ),
    FittingCreate(
        name="Тройник 110х50х45",
        groupname="Тройники",
        image_path="fittings/Group 55.png",
        material_id="104",
    ),
    FittingCreate(
        name="Тройник 110х110х45",
        groupname="Тройники",
        image_path="fittings/Group 56.png",
        material_id="103",
    ),
    FittingCreate(
        name="Тройник 125х110х87",
        groupname="Тройники",
        image_path="fittings/Group 54.png",
        material_id="107",
    ),
    FittingCreate(
        name="Тройник 125х110х45",
        groupname="Тройники",
        image_path="fittings/Group 58.png",
        material_id="108",
    ),
    FittingCreate(
        name="Крестовина 110х110х50х87 Левая",
        groupname="Крестовины",
        image_path="fittings/Group 59.png",
        material_id="201",
    ),
    FittingCreate(
        name="Крестовина 110х110х50х87 Правая",
        groupname="Крестовины",
        image_path="fittings/Group 60.png",
        material_id="202",
    ),
    FittingCreate(
        name="Тройник 110х110х87",
        groupname="Крестовины",
        image_path="fittings/Group 10.png",
        material_id=None,
    ),
    FittingCreate(
        name="Крестовина 110х110х50х89",
        groupname="Крестовины",
        image_path="fittings/Group 9.png",
        material_id="203",  # ALSO SHOULD BE Left/Right
    ),
    FittingCreate(
        name="Крестовина 110х110х110х87",
        groupname="Крестовины",
        image_path="fittings/Group 8.png",
        material_id="205",
    ),
    FittingCreate(
        name="Крестовина 110х110х50х87",
        groupname="Крестовины",
        image_path="fittings/Group 7.png",
        material_id=None,
    ),
    FittingCreate(
        name="Крестовина 125х110х110х87",
        groupname="Крестовины",
        image_path="fittings/Group 6.png",
        material_id="206",
    ),
    FittingCreate(
        name="Патрубок компенсационный D50",
        groupname="Патрубки",
        image_path="fittings/Group 5.png",
    ),
    FittingCreate(
        name="Патрубок компенсационный D110",
        groupname="Патрубки",
        image_path="fittings/Group 4.png",
    ),
    FittingCreate(
        name="Патрубок компенсационный D125",
        groupname="Патрубки",
        image_path="fittings/Group 3.png",
    ),
    FittingCreate(
        name="Ревизия 50", groupname="Ревизия", image_path="fittings/Group 2.png"
    ),
    FittingCreate(
        name="Ревизия 110", groupname="Ревизия", image_path="fittings/Group 1.png"
    ),
    FittingCreate(
        name="Ревизия 125", groupname="Ревизия", image_path="fittings/Group 11.png"
    ),
    FittingCreate(
        name="Труба прямая под сифон 40х40L=200мм",
        groupname="Фановая труба",
        image_path="fittings/Group 12.png",
        material_id="502",
    ),
    FittingCreate(
        name="Труба фановая 110х45",
        groupname="Фановая труба",
        image_path="fittings/Group 13.png",
        material_id="500",
    ),
    FittingCreate(
        name="Труба фановая 250",
        groupname="Фановая труба",
        image_path="fittings/Group 14.png",
        material_id=None,
    ),
    FittingCreate(
        name="Редукция короткая 50х40",
        groupname="Редукция",
        image_path="fittings/Group 15.png",
        material_id="402",
    ),
    FittingCreate(
        name="Редукция 50х32",
        groupname="Редукция",
        image_path="fittings/Group 16.png",
        material_id=None,
    ),
    FittingCreate(
        name="Редукция 50х40",
        groupname="Редукция",
        image_path="fittings/Group 17.png",
        material_id="400",
    ),
    FittingCreate(
        name="Редукция 110х50",
        groupname="Редукция",
        image_path="fittings/Group 18.png",
        material_id="401",
    ),
    FittingCreate(
        name="Редукция с увеличением 32х40",
        groupname="Редукция",
        image_path="fittings/Group 20.png",
        material_id=None,
    ),
    FittingCreate(
        name="Редукция 32х50",
        groupname="Редукция",
        image_path="fittings/Group 19.png",
        material_id=None,
    ),
    FittingCreate(
        name="Редукция 110х50",
        groupname="Редукция",
        image_path="fittings/Group 31.png",
        material_id="403",
    ),
    FittingCreate(
        name="Отвод 110/50х45 выход вправо",
        groupname="Отвод фронтальный",
        image_path="fittings/Group 30.png",
    ),
    FittingCreate(
        name="Отвод ПВХ-87 D110",
        groupname="Отвод фронтальный",
        image_path="fittings/Group 29.png",
    ),
    FittingCreate(
        name="Отвод ПВХ 110/50х87 выход вверх",
        groupname="Отвод фронтальный",
        image_path="fittings/Group 28.png",
    ),
    FittingCreate(
        name="Отвод ПВХ 110/50х87 выход влево",
        groupname="Отвод фронтальный",
        image_path="fittings/Group 27.png",
    ),
    FittingCreate(
        name="Отвод ПВХ 110/50х87 выход вправо",
        groupname="Отвод фронтальный",
        image_path="fittings/Group 26.png",
    ),
    FittingCreate(
        name="Отвод ПВХ 110х45 с выходом 50, левый",
        groupname="Отводы",
        image_path="fittings/Group 25.png",
    ),
    FittingCreate(
        name="Отвод ПВХ 110х45 с выходом 50, правый",
        groupname="Отводы",
        image_path="fittings/Group 24.png",
    ),
    FittingCreate(
        name="Отвод ПВХ-32х15",
        groupname="Отводы",
        image_path="fittings/Group 23.png",
    ),
    FittingCreate(
        name="Отвод ПВХ-32х30", groupname="Отводы", image_path="fittings/Group 22.png"
    ),
    FittingCreate(
        name="Отвод ПВХ-32х45", groupname="Отводы", image_path="fittings/Group 32.png"
    ),
    FittingCreate(
        name="Отвод ПВХ-32х67", groupname="Отводы", image_path="fittings/Group 33.png"
    ),
    FittingCreate(
        name="Отвод ПВХ-32х87", groupname="Отводы", image_path="fittings/Group 34.png"
    ),
    FittingCreate(
        name="Отвод ПВХ-32х90", groupname="Отводы", image_path="fittings/Group 35.png"
    ),
    FittingCreate(
        name="Отвод ПВХ-87 D40",
        groupname="Отводы",
        image_path="fittings/Group 36.png",
        material_id="310",
    ),
    FittingCreate(
        name="Отвод ПВХ-45 D40",
        groupname="Отводы",
        image_path="fittings/Group 37.png",
        material_id="309",
    ),
    FittingCreate(
        name="Отвод ПВХ-40х67",
        groupname="Отводы",
        image_path="fittings/Group 38.png",
        material_id="311",
    ),
    FittingCreate(
        name="Отвод ПВХ-50х15",
        groupname="Отводы",
        image_path="fittings/Group 39.png",
        material_id="308",
    ),
    FittingCreate(
        name="Отвод ПВХ-45 D50",
        groupname="Отводы",
        image_path="fittings/Group 40.png",
        material_id="304",
    ),
    FittingCreate(
        name="Отвод ПВХ-50х30",
        groupname="Отводы",
        image_path="fittings/Group 41.png",
        material_id="307",
    ),
    FittingCreate(
        name="Отвод ПВХ-50х67",
        groupname="Отводы",
        image_path="fittings/Group 42.png",
        material_id="306",
    ),
    FittingCreate(
        name="Отвод ПВХ-50х87",
        groupname="Отводы",
        image_path="fittings/Group 43.png",
        material_id="305",
    ),
    FittingCreate(
        name="Отвод ПВХ-110х15",
        groupname="Отводы",
        image_path="fittings/Group 44.png",
        material_id=None,
    ),
    FittingCreate(
        name="Отвод ПВХ-110х30",
        groupname="Отводы",
        image_path="fittings/Group 45.png",
        material_id="303",
    ),
    FittingCreate(
        name="Отвод ПВХ-110х45",
        groupname="Отводы",
        image_path="fittings/Group 46.png",
        material_id="300",
    ),
    FittingCreate(
        name="Отвод ПВХ-110х67,5",
        groupname="Отводы",
        image_path="fittings/Group 47.png",
        material_id="302",
    ),
    FittingCreate(
        name="Отвод ПВХ-110х87",
        groupname="Отводы",
        image_path="fittings/Group 48.png",
        material_id="301",
    ),
    FittingCreate(
        name="Отвод ПВХ-90 D110", groupname="Отводы", image_path="fittings/Group 49.png"
    ),
    FittingCreate(
        name="Отвод ПВХ-45 D125", groupname="Отводы", image_path="fittings/Group 50.png"
    ),
]
