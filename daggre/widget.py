"""ipywidgets host: render a daggre Graph in Jupyter via anywidget over the widget's comm.

`Widget(graph)` hosts the graph in a `transports.Session`/`Server`; the transports wire rides the
widget's comm (the same protocol as the web host — only the transport differs). The widget object is
itself the transports "connection". Live updates are pushed by a background pump on the kernel's event
loop; outside a loop, call `widget.flush()`. anywidget makes this an ordinary ipywidgets DOMWidget, so
it composes with any ipywidgets layout.
"""

import anywidget
import asyncio
import traitlets
import transports
from pathlib import Path
from typing import Any, Optional

STATIC = Path(__file__).parent / "static"
_WASM = (STATIC / "transports_bg.wasm").read_bytes()


class Widget(anywidget.AnyWidget):
    _esm = STATIC / "anywidget.js"
    # transports' wasm core, shipped to the frontend as a synced byte buffer (no served .wasm needed)
    _wasm = traitlets.Bytes(_WASM).tag(sync=True)

    def __init__(self, graph: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._graph = graph
        self._session = transports.Session()
        self._session.host(graph)
        self._server = transports.Server(self._session)
        self._opened = False
        self._pump_task: Optional[asyncio.Task] = None
        self.on_msg(self._on_msg)

    def _on_msg(self, _widget: Any, content: Any, _buffers: Any) -> None:
        if not isinstance(content, dict):
            return
        if content.get("ready") and not self._opened:
            self._opened = True
            for wire in self._server.open(self):  # opening snapshots
                self.send({"wire": wire})
            self._start_pump()
        elif "wire" in content:  # client -> server (e.g. edits); echoed authoritatively
            for conn, msgs in self._server.recv(self, content["wire"]).items():
                for m in msgs:
                    conn.send({"wire": m})

    def flush(self) -> None:
        """Push pending graph changes to the frontend now (use when no event loop is pumping)."""
        for conn, msgs in self._server.flush().items():
            for m in msgs:
                conn.send({"wire": m})

    def close(self, *args: Any, **kwargs: Any) -> None:
        """Cancel the background pump and drop the transports connection, then close the widget."""
        if self._pump_task is not None:
            self._pump_task.cancel()
            self._pump_task = None
        self._server.close(self)
        super().close(*args, **kwargs)

    def _start_pump(self) -> None:
        if self._pump_task is not None:
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return  # no kernel loop running; changes go out on explicit flush()
        self._pump_task = loop.create_task(self._pump())

    async def _pump(self) -> None:
        while True:
            await asyncio.sleep(0.1)
            self.flush()
