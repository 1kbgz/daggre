from .base import BaseModel
from .common import Shape


class Node(BaseModel):
    shape: Shape = "rect"
    tooltip: str = ""
    color: str = "black"
    backgroundColor: str = "rgba(255, 255, 255, 0)"

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        # by identity
        return isinstance(other, Node) and self.id == other.id

    def __lt__(self, other: object) -> bool:
        # for sorting
        if isinstance(other, Node):
            return self.name < other.name
        return NotImplemented

    def __repr__(self) -> str:
        return f"Node[{self.name or self.id[:10]}]"
