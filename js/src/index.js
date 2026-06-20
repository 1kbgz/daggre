// daggre frontend: render a transports-synced Graph with daggre's own <dagre-graph> element.
//
// daggre owns the rendering (the element + its shapes). The Python `Graph` is a transports model; this
// module mirrors it with a transports `Client` and maps it onto the element. The host (vanilla web
// server, ipywidgets/anywidget, or a spaday app) only provides a connection; the mapping + rendering
// here are shared. No spaday is needed for the vanilla/widget hosts — only the spaday-app host uses
// spaday's runtime to mount its tree (which may contain this element).
import "./dagre-graph.js"; // defines <dagre-graph>
import { Client, fromValue, wasm } from "@1kbgz/transports";

let _wasmReady;
/** Initialize transports' wasm core once (idempotent). `wasmUrl` -> transports_bg.wasm. */
export function initWasm(wasmUrl) {
  _wasmReady = _wasmReady || wasm.default({ module_or_path: wasmUrl });
  return _wasmReady;
}

// Map a daggre Graph wire value (untagged) onto <dagre-graph>'s direction/nodes/edges props.
function toGraphProps(model) {
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
  return { direction: (model && model.direction) || "top-to-bottom", nodes, edges };
}

/**
 * Bind an existing <dagre-graph> element (e.g. one a spaday app already mounted) to a transports
 * `Client`. Returns `{ el, paint }`; the caller drives `paint` after each snapshot/patch is applied.
 */
export function attach(el, { client, modelId } = {}) {
  const paint = () => {
    const id = modelId != null ? modelId : client.ids()[0];
    if (id == null) return;
    const model = fromValue(client.value(id));
    if (!model) return;
    const props = toGraphProps(model);
    el.direction = props.direction;
    el.nodes = props.nodes;
    el.edges = props.edges;
  };
  return { el, paint };
}

/** Create a <dagre-graph> in `container` and bind it (the standalone case). */
export function render(container, opts = {}) {
  const el = document.createElement("dagre-graph");
  el.style.height = el.style.height || "100%";
  container.appendChild(el);
  return attach(el, { ...opts });
}

/** Convenience for the vanilla-webserver host: open a transports WebSocket, mirror, and render. */
export async function connect(container, { wsUrl, wasmUrl }) {
  await initWasm(wasmUrl);
  const client = new Client();
  const { el, paint } = render(container, { client });
  const ws = new WebSocket(wsUrl);
  ws.binaryType = "arraybuffer";
  ws.addEventListener("message", (event) => {
    client.recv(typeof event.data === "string" ? event.data : new Uint8Array(event.data));
    paint();
  });
  return { client, ws, el };
}

export { Client, fromValue, wasm };
