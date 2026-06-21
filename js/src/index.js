// daggre frontend: render a transports-synced Graph with daggre's own <dagre-graph> element.
//
// daggre owns the rendering (the element + its shapes). The Python `Graph` is a transports model; this
// module mirrors it with a transports `Client` and maps it onto the element. The host (vanilla web
// server, ipywidgets/anywidget, or a spaday app) only provides a connection; the mapping + rendering
// here are shared. No spaday is needed for the vanilla/widget hosts — only the spaday-app host uses
// spaday's runtime to mount its tree (which may contain this element).
import "./dagre-graph"; // defines <dagre-graph>
// eslint-disable-next-line import/no-unresolved
import { Client, fromValue, wasm } from "@1kbgz/transports";

import { toGraphProps } from "./map";

let wasmReady;
/** Initialize transports' wasm core once (idempotent). `wasmUrl` -> transports_bg.wasm. */
export function initWasm(wasmUrl) {
  wasmReady = wasmReady || wasm.default({ module_or_path: wasmUrl });
  return wasmReady;
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
    /* eslint-disable no-param-reassign */
    el.direction = props.direction;
    el.nodes = props.nodes;
    el.edges = props.edges;
    /* eslint-enable no-param-reassign */
  };
  return { el, paint };
}

/** Create a <dagre-graph> in `container` and bind it (the standalone case). */
export function render(container, opts = {}) {
  const el = document.createElement("dagre-graph");
  if (!el.style.height) el.style.height = "100%";
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
    client.recv(
      typeof event.data === "string" ? event.data : new Uint8Array(event.data),
    );
    paint();
  });
  return { client, ws, el };
}

export { Client, fromValue, wasm };
