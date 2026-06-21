import { toGraphProps } from "../src/map";

describe("toGraphProps", () => {
  test("maps a Graph wire value onto dagre-graph props", () => {
    const model = {
      direction: "left-to-right",
      nodes: {
        a: { name: "a", label: "A", shape: "house", color: "red" },
        b: { name: "b", backgroundColor: "lightblue" },
      },
      edges: [
        { from_: { name: "a" }, to_: { name: "b" }, line: "dash", arrowhead: "vee" },
      ],
    };
    const props = toGraphProps(model);
    expect(props.direction).toBe("left-to-right");
    expect(props.nodes).toEqual([
      { id: "a", label: "A", shape: "house", color: "red", backgroundColor: undefined },
      { id: "b", label: "b", shape: undefined, color: undefined, backgroundColor: "lightblue" },
    ]);
    expect(props.edges).toEqual([{ from: "a", to: "b", line: "dash", arrowhead: "vee" }]);
  });

  test("defaults direction and tolerates an empty model", () => {
    expect(toGraphProps({})).toEqual({ direction: "top-to-bottom", nodes: [], edges: [] });
  });
});
