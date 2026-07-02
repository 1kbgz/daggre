from typing import Optional

from .base import BaseModel
from .common import Arrowhead, LabelPosition, Line
from .node import Node


class Edge(BaseModel):
    from_: Node
    to_: Node
    tooltip: str = ""
    line: Line = "solid"
    labelposition: LabelPosition = "r"
    labeloffset: Optional[float] = None
    arrowhead: Arrowhead = "vee"

    def __lt__(self, other: "Edge") -> bool:
        return self.from_.name < other.from_.name or self.to_.name < other.to_.name

    def __repr__(self) -> str:
        return f"Edge[{self.from_.name} -> {self.to_.name}]"
