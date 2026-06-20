// daggre's custom dagre-d3 shapes/arrows. Baked into daggre's own <dagre-graph> element (no cross-repo
// extension hook). They only need the d3 selection the renderer hands them plus dagre-d3-es's geometry
// helper for the polygon intersect.
import { intersect } from "dagre-d3-es";

const house = (parent, bbox, node) => {
  const w = bbox.width;
  const h = bbox.height;
  const points = [
    { x: 0, y: 0 },
    { x: w, y: 0 },
    { x: w, y: -h },
    { x: w / 2, y: (-h * 3) / 2 },
    { x: 0, y: -h },
  ];
  const shapeSvg = parent
    .insert("polygon", ":first-child")
    .attr("points", points.map((d) => `${d.x},${d.y}`).join(" "))
    .attr("transform", `translate(${-w / 2},${(h * 3) / 4})`);
  // eslint-disable-next-line no-param-reassign
  node.intersect = (point) => intersect.polygon.intersectPolygon(node, points, point);
  return shapeSvg;
};

const hollowpoint = (parent, id, edge, type) => {
  const marker = parent
    .append("marker")
    .attr("id", id)
    .attr("viewBox", "0 0 10 10")
    .attr("refX", 9)
    .attr("refY", 5)
    .attr("markerUnits", "strokeWidth")
    .attr("markerWidth", 8)
    .attr("markerHeight", 6)
    .attr("orient", "auto");
  const path = marker
    .append("path")
    .attr("d", "M 0 0 L 10 5 L 0 10 z")
    .style("stroke-width", 1)
    .style("stroke-dasharray", "1,0")
    .style("fill", "#fff")
    .style("stroke", "#333");
  path.attr("style", edge[`${type}Style`]);
  return marker;
};

export const customShapes = { house };
export const customArrows = { hollowpoint };
