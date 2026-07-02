from pytest import fixture

from daggre import Edge, Graph, Node


@fixture
def a_node():
    return Node(name="a")


@fixture
def b_node():
    return Node(name="b")


@fixture
def a_to_b_edge(a_node, b_node):
    return Edge(from_=a_node, to_=b_node)


@fixture
def new_graph():
    return Graph()
