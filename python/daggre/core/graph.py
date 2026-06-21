from pydantic import Field
from typing import Any, Dict, List, Optional, Union

from .base import BaseModel
from .common import Direction
from .edge import Edge
from .exceptions import MalformedArgument
from .node import Node


class Graph(BaseModel):
    directed: bool = True
    multigraph: bool = False
    compound: bool = False
    direction: Direction = "top-to-bottom"
    edges: List[Edge] = Field(default_factory=list)
    nodes: Dict[str, Node] = Field(default_factory=dict)

    def addNode(self, node: Union[str, Node], **node_kwargs: Any) -> Node:
        if isinstance(node, str):
            # a bare reference (e.g. from addEdge) to an existing node: don't clobber its styling
            if node in self.nodes and not node_kwargs:
                return self.nodes[node]
            node_kwargs["name"] = node
            return self.addNode(Node(**node_kwargs))
        if isinstance(node, Node):
            # in-place upsert; a hosting transports Session observes it (bigbrother, deepstate)
            self.nodes[node.name] = node
            return self.nodes[node.name]
        raise MalformedArgument(f"Bad argument type: {node} {type(node)}")

    def addEdge(
        self,
        edge_or_node_from_: Union[str, Edge, Node],
        to_: Optional[Union[str, Node]] = None,
        **edge_kwargs: Any,
    ) -> None:
        # already an Edge: ensure both endpoints are in the graph, then record it
        if isinstance(edge_or_node_from_, Edge):
            edge = edge_or_node_from_
            self.addNode(edge.from_)
            self.addNode(edge.to_)
            self.edges.append(edge)
            return

        # from + to form: resolve both endpoints, then recurse on the built Edge
        if isinstance(edge_or_node_from_, str):
            node1: Node = self.addNode(edge_or_node_from_)
        elif isinstance(edge_or_node_from_, Node):
            node1 = edge_or_node_from_
        else:
            raise MalformedArgument(f"Bad argument type for `edge_or_node_from_`: {edge_or_node_from_} {type(edge_or_node_from_)}")

        if isinstance(to_, str):
            node2: Node = self.addNode(to_)
        elif isinstance(to_, Node):
            node2 = to_
        else:
            raise MalformedArgument(f"Bad argument type for `to_`: {to_} {type(to_)}")

        self.addEdge(Edge(from_=node1, to_=node2, **edge_kwargs))
