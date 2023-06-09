import re
from typing import List, Optional

from src.trace_builder.geometry import l1_distance
from src.trace_builder.model import Point, Segment


class Stuff:
    def __init__(
        self,
        name: str,
        coordinates: Optional[Point] = None,
        projection: Optional[Point] = None,
        nearest_segment: Optional[Segment] = None,
        l1_projection: Optional[float] = None,
        riser_l1_distance: Optional[float] = None,
        height: Optional[float] = None,
    ):
        self.id = id
        self.name = name
        self.coordinates = coordinates
        self.projection = projection
        self.nearest_segment = nearest_segment
        self.l1_projection = l1_projection
        self.riser_l1_distance = riser_l1_distance
        self.height = height
        self.is_toilet = self._is_toilet(self.name) if self.name else False

    def _is_toilet(self, stuff) -> bool:
        return True if bool(re.search(".*[Уу]нитаз.*", stuff)) else False


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
        stuff_point: Optional[List[Stuff]] = None,
        after_toilet: Optional[bool] = False,
        cumm_slope_shift: int = 0,
    ):
        self.coordinates = wall
        self.start = self.coordinates.start
        self.end = self.coordinates.end
        self.has_toilet = has_toilet
        self.has_stuff = has_stuff
        self.entery_wall = entery_wall
        self.with_riser = with_riser
        self.max_length_stuff = max_length_stuff
        self.path2wall_with_riser = path2wall_with_riser
        self.height = None
        self.stuff_point = stuff_point
        self.start_pipe_point = None
        self.after_toilet = after_toilet
        self.cumm_slope_shift = cumm_slope_shift

        self.length = l1_distance(self.coordinates.start, self.coordinates.end)

    def comput_start_wall(self):
        if not self.start_pipe_point:
            return
        pass


class Pipe:
    def __init__(
        self,
        coordinates: Point,
        is_toilet: bool = False,
        is_start: bool = False,
        is_end: bool = False,
        with_riser: bool = False,
        is_wall_end: bool = False,
        is_wall_start: bool = False,
        stuff: Optional[Stuff] = None,
        after_reduction: bool = False,
        cumm_slope_shift: int = 0,
    ):
        self.coordinates = coordinates
        self.is_toilet = is_toilet
        self.is_start = is_start
        self.is_end = is_end
        self.with_riser = with_riser
        self.stuff = stuff
        self.is_wall_end = is_wall_end
        self.is_wall_start = is_wall_start
        self.after_reduction = after_reduction
        self.cumm_slope_shift = cumm_slope_shift
