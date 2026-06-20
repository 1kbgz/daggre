// daggre's <dagre-graph> custom element: wraps dagre-d3-es as a web component whose props
// (direction/nodes/edges) drive the renderer. daggre owns this (it's the only consumer, and its
// house/hollowpoint shapes are baked in here). spaday's runtime can mount it like any element, but the
// element itself needs no spaday.
import * as d3 from "d3";
import { graphlib, render as makeRender } from "dagre-d3-es";

import { customArrows, customShapes } from "./shapes.js";

const RANKDIR = {
  "top-to-bottom": "TB",
  "bottom-to-top": "BT",
  "left-to-right": "LR",
  "right-to-left": "RL",
};

export class DagreGraph extends HTMLElement {
  constructor() {
    super();
    this.renderer = makeRender();
    Object.assign(this.renderer.shapes(), customShapes);
    Object.assign(this.renderer.arrows(), customArrows);
    this._direction = "top-to-bottom";
    this._nodes = [];
    this._edges = [];
  }

  connectedCallback() {
    if (!this.style.display) this.style.display = "block";
    if (!this.style.height) this.style.height = "400px";
    this.svg = d3.select(this).append("svg").attr("width", "100%").attr("height", "100%");
    this.inner = this.svg.append("g");
    this.zoom = d3.zoom().on("zoom", (event) => this.inner && this.inner.attr("transform", event.transform));
    this.svg.call(this.zoom);
    this.draw();
  }

  disconnectedCallback() {
    if (this.svg) this.svg.remove();
    this.svg = undefined;
    this.inner = undefined;
    this.zoom = undefined;
  }

  get direction() {
    return this._direction;
  }
  set direction(value) {
    this._direction = value || "top-to-bottom";
    this.draw();
  }

  get nodes() {
    return this._nodes;
  }
  set nodes(value) {
    this._nodes = value || [];
    this.draw();
  }

  get edges() {
    return this._edges;
  }
  set edges(value) {
    this._edges = value || [];
    this.draw();
  }

  build() {
    const g = new graphlib.Graph({ directed: true });
    g.setGraph({
      rankdir: RANKDIR[this._direction] || "TB",
      nodesep: 50,
      ranksep: 50,
      marginx: 20,
      marginy: 20,
    });
    g.setDefaultEdgeLabel(() => ({}));

    for (const n of this._nodes) {
      const id = String(n.id != null ? n.id : n.name != null ? n.name : "");
      if (!id) continue;
      const { id: _id, name: _name, color, backgroundColor, ...rest } = n;
      const opts = { label: n.label != null ? n.label : id, ...rest };
      if (color) opts.labelStyle = `fill: ${color};`;
      if (backgroundColor) opts.style = `fill: ${backgroundColor};`;
      g.setNode(id, opts);
    }

    for (const e of this._edges) {
      const from = String(e.from != null ? e.from : e.source != null ? e.source : "");
      const to = String(e.to != null ? e.to : e.target != null ? e.target : "");
      if (!from || !to) continue;
      const { from: _f, to: _t, source: _s, target: _tg, line, ...rest } = e;
      const opts = { curve: d3.curveBasis, ...rest };
      if (line === "dash") opts.style = `${opts.style || ""}stroke-dasharray: 5, 5;`;
      g.setEdge(from, to, opts);
    }
    return g;
  }

  draw() {
    if (!this.inner) return;
    const g = this.build();
    if (g.nodeCount() === 0) {
      this.inner.selectAll("*").remove();
      return;
    }
    this.renderer(this.inner, g);
    this.fit(g);
  }

  fit(g) {
    if (!this.svg || !this.zoom) return;
    const w = this.clientWidth || 1;
    const h = this.clientHeight || 1;
    const graph = g.graph();
    const gw = graph.width || 1;
    const gh = graph.height || 1;
    const scale = Math.min(w / gw, h / gh, 1.5) * 0.9 || 1;
    const tx = (w - gw * scale) / 2;
    const ty = (h - gh * scale) / 2;
    this.svg.call(this.zoom.transform, d3.zoomIdentity.translate(tx, ty).scale(scale));
  }
}

if (!customElements.get("dagre-graph")) {
  customElements.define("dagre-graph", DagreGraph);
}
