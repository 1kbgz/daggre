from typing import Literal

# Graph
Direction = Literal["left-to-right", "right-to-left", "top-to-bottom", "bottom-to-top"]

# Edge
Arrowhead = Literal["normal", "vee", "undirected", "hollowpoint"]
LabelPosition = Literal["r", "c", "l"]
Line = Literal["solid", "dash"]

# Node
Shape = Literal["rect", "circle", "ellipse", "diamond", "house"]
