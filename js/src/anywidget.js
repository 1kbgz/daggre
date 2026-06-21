// anywidget entry: render the daggre graph inside a Jupyter/ipywidgets widget.
//
// Reuses the shared bootstrap (`render`) — only the transport differs: instead of a WebSocket, the
// transports wire rides the widget's comm (Python `widget.send({wire})` -> `msg:custom`). The wasm is
// delivered as a synced bytes traitlet, so a notebook needs no separately served .wasm file.
import { render as daggreRender, wasm, Client } from "./index";

export default {
  async render({ model, el }) {
    // eslint-disable-next-line no-param-reassign
    if (!el.style.height) el.style.height = "500px";

    const bytes = model.get("_wasm");
    const buffer = bytes && bytes.buffer ? bytes.buffer : bytes;
    await wasm.default({ module_or_path: buffer });

    const client = new Client();
    const { paint } = daggreRender(el, { client });

    model.on("msg:custom", (msg) => {
      if (msg && msg.wire != null) {
        client.recv(msg.wire);
        paint();
      }
    });

    // tell the kernel the view is ready for the opening snapshot
    model.send({ ready: true });
  },
};
