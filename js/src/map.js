// Pure mapping (no DOM): a daggre Graph wire value (untagged) -> <dagre-graph> props. Kept separate
// from the element/bootstrap so it's unit-testable in node; the browser bundle is tested in a browser.
export function toGraphProps(model) {
  const nodes = Object.values((model && model.nodes) || {}).map((n) => ({
    id: n.name,
    label: n.label || n.name,
    shape: n.shape,
    color: n.color,
    backgroundColor: n.backgroundColor,
  }));
  const edges = ((model && model.edges) || []).map((e) => ({
    from: e.from_.name,
    to: e.to_.name,
    line: e.line,
    arrowhead: e.arrowhead,
  }));
  return {
    direction: (model && model.direction) || "top-to-bottom",
    directed: model ? model.directed !== false : true,
    multigraph: Boolean(model && model.multigraph),
    compound: Boolean(model && model.compound),
    nodes,
    edges,
  };
}
