from daggre import Graph


def test_graph_generator_helper():
    graph = Graph(direction="left-to-right")

    # function to add nodes to graph
    SCALE = 10
    begin = 0

    while begin < 30:
        for i in range(begin, begin + SCALE):
            if i > 0:
                if i % 2 == 0:
                    graph.addNode(f"test{i}", color="red")
                else:
                    graph.addNode(f"test{i}", backgroundColor="lightblue")
                graph.addEdge(f"test{i - 1}", f"test{i}")
            else:
                graph.addNode(f"test{i}", backgroundColor="lightgreen")

            if i > 2:
                for j in range(4):
                    if i % (j + 2) == 0:
                        graph.addEdge(
                            f"test{int(i / (j + 2))}",
                            f"test{i}",
                            arrowhead="vee",
                            line="dash",
                        )
        begin += SCALE
    assert len(graph.nodes) == 30
    assert len(graph.edges) == 63
