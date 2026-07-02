__version__ = "0.1.1"

from .core import Arrowhead, Direction, Edge, Graph, LabelPosition, Line, Node, Shape

__all__ = ["Arrowhead", "Direction", "Edge", "Graph", "LabelPosition", "Line", "Node", "Shape", "serve", "Widget"]


def __getattr__(name: str):
    # Host adapters are lazily imported so the core domain needn't pull starlette / anywidget.
    if name == "serve":
        from .web import serve

        return serve
    if name == "Widget":
        from .widget import Widget

        return Widget
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
