"""Vanilla web host: serve a daggre `Graph` over transports to a browser, no notebook required.

`serve(graph)` returns a ready Starlette app (so it drops into uvicorn, or `mount`s into an existing
FastAPI/Starlette app). The graph is hosted in a `transports.Session`; mutating it from anywhere
(including a background task) is broadcast to every connected browser, which renders it with the
daggre frontend bundle (spaday's `<dagre-graph>`).
"""

import asyncio
from collections.abc import Callable, Coroutine
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import transports
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Mount, Route, WebSocketRoute
from starlette.staticfiles import StaticFiles

STATIC = Path(__file__).parent / "static"

_PAGE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <style>
      html, body {{ margin: 0; height: 100%; font-family: system-ui, sans-serif; }}
      #graph {{ width: 100%; height: 100%; }}
      .node rect, .node circle, .node ellipse, .node polygon {{ stroke-width: 1.5px; }}
      .edgePath path {{ stroke: #333; fill: none; stroke-width: 1.5px; }}
    </style>
  </head>
  <body>
    <div id="graph"></div>
    <script type="module">
      import {{ connect }} from "/static/index.js";
      connect(document.getElementById("graph"), {{
        wsUrl: `${{location.protocol === "https:" ? "wss:" : "ws:"}}//${{location.host}}/ws`,
        wasmUrl: "/static/transports_bg.wasm",
      }});
    </script>
  </body>
</html>"""


def serve(
    graph: Any,
    *,
    title: str = "daggre",
    background: Callable[[Any], Coroutine[Any, Any, None]] | None = None,
) -> Starlette:
    """Build a Starlette app that serves `graph` live over transports.

    `background`, if given, is an async callable run with the graph as its argument for the app's
    lifetime — use it to mutate the graph over time (the mutations stream to every client).
    """
    session = transports.Session()
    session.host(graph)
    server = transports.Server(session)

    @asynccontextmanager
    async def lifespan(app: Starlette):
        tasks = [asyncio.create_task(transports.autosync(server))]
        if background is not None:
            tasks.append(asyncio.create_task(background(graph)))
        try:
            yield
        finally:
            for task in tasks:
                task.cancel()

    async def index(_request):
        return HTMLResponse(_PAGE.format(title=title))

    return Starlette(
        routes=[
            Route("/", index),
            WebSocketRoute("/ws", transports.ws_endpoint(server)),
            Mount("/static", StaticFiles(directory=STATIC)),
        ],
        lifespan=lifespan,
    )
