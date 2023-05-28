from typing import Optional, List
from model import Segment, Point
from geometry import l1_distance
import re


class Wall:
    def __init__(
        self,
        wall: Segment,
        has_toilet: bool = False,
        has_stuff: bool = False,
        entery_wall: bool = False,
        with_riser: bool = False,
        max_length_stuff: Optional[float] = None,
        path2wall_with_riser: Optional[List] = None,
        stuff_point: Optional[List[Point]] = None,
    ):
        self.wall = wall
        self.start = self.wall.start
        self.end = self.wall.end
        self.has_toilet = has_toilet
        self.has_stuff = has_stuff
        self.entery_wall = entery_wall
        self.with_riser = with_riser
        self.max_length_stuff = max_length_stuff
        self.path2wall_with_riser = path2wall_with_riser
        self.height = None
        self.stuff_point = stuff_point
        self.start_pipe_point = None

        self.length = l1_distance(self.wall.start, self.wall.end)

    def comput_start_wall(self):
        if not self.start_pipe_point:
            return
        pass


class Stuff:
    def __init__(
        self,
        name: str,
        coordinates: Point,
        projection: Point,
        nearest_segment: Segment,
        l1_projection: float,
        riser_l1_distance: float,
        height: float,
    ):
        self.name = name
        self.coordinates = coordinates
        self.projection = projection
        self.nearest_segment = nearest_segment
        self.l1_projection = l1_projection
        self.riser_l1_distance = riser_l1_distance
        self.height = height
        self.is_toilet = _is_toilet(self.name)


def _is_toilet(stuff) -> bool:
    return True if bool(re.search(".*[Уу]нитаз.*", stuff)) else False


class Pipe:
    def __init__(
        self,
        coordinates: Point,
        is_toilet: bool = False,
        is_start: bool = False,
        is_end: bool = False,
        with_riser: bool = False,
        stuff: Optional[Stuff] = None,
    ):
        self.coordinates = coordinates
        self.is_toilet = is_toilet
        self.is_start = is_start
        self.is_end = is_end
        self.with_riser = with_riser
        self.stuff = stuff
