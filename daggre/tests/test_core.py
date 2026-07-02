from daggre import Graph


class TestBasic:
    def test_node_repr(self, a_node):
        assert repr(a_node) == "Node[a]"

    def test_edge_repr(self, a_to_b_edge):
        assert repr(a_to_b_edge) == "Edge[a -> b]"

    def test_basic_construction(self, a_node, b_node, a_to_b_edge, new_graph):
        g = new_graph
        g.addNode(a_node)
        g.addNode(b_node)
        g.addEdge(a_to_b_edge)
        g.addEdge(a_node, b_node)

        assert sorted(list(g.nodes.values())) == [a_node, b_node]
        assert len(g.edges) == 2
        assert a_to_b_edge in g.edges

    def test_basic_construction_no_copies(self, a_node, b_node, a_to_b_edge, new_graph):
        g = new_graph
        g.addEdge(a_to_b_edge)

        assert a_node == new_graph.nodes["a"]
        assert id(a_node) == id(new_graph.nodes["a"])
        assert id(a_node) == id(a_to_b_edge.from_)

        assert b_node == new_graph.nodes["b"]
        assert id(b_node) == id(new_graph.nodes["b"])
        assert id(b_node) == id(a_to_b_edge.to_)

    def test_basic_construction_nodes_included_when_edge_added(self, a_node, b_node, a_to_b_edge, new_graph):
        g = new_graph
        g.addEdge(a_to_b_edge)

        assert sorted(list(g.nodes.values())) == [a_node, b_node]
        assert len(g.edges) == 1
        assert a_to_b_edge in g.edges

    def test_node_construction_options(self, new_graph):
        new_graph.addNode("test", color="red")
        new_graph.addNode("test2", backgroundColor="lightblue")

    def test_edge_construction_options(self, a_node, b_node, new_graph):
        new_graph.addNode(a_node)
        new_graph.addNode(b_node)
        new_graph.addEdge("a", "b", arrowhead="vee", line="dash")

    def test_graph_construction_options(self):
        Graph(direction="left-to-right")
