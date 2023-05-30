from dataclasses import dataclass
from typing import List, Tuple, Union


@dataclass
class Node:
    name: str
    material_id: int
    length: int = None
    is_start: bool = False
    is_end: bool = False
    is_troinik: bool = False
    is_inside_troinik: bool = False
    uniq_end: int = None


class PipeGraph:
    def __init__(self, nodes=None):
        if not nodes:
            self.nodes = []
        elif isinstance(nodes, list):
            self.nodes = nodes
        else:
            self.nodes = [nodes]
        self.uniq_end = 1

    def add_node(self, nodes: Union[List[Node], Node], end: bool = False):
        if isinstance(nodes, list):
            if end:
                for node in nodes:
                    node.uniq_end = self.uniq_end
                self.uniq_end += 1
            self.nodes.extend(nodes)
        else:
            if end:
                nodes.uniq_end = self.uniq_end
                self.uniq_end += 1
            self.nodes.append(nodes)
