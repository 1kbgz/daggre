"""daggre inside a spaday app: a spaday component tree (heading + graph) authored in Python, with the
daggre Graph synced over transports.

The shell is authored with spaday (`element("dagre-graph")`); the browser mounts it with the spaday
runtime and daggre binds the mounted <dagre-graph> to a transports `Client`. Run (needs
spaday + daggre + transports on the path; spaday built)::

    PYTHONPATH=../../python:<spaday repo> python examples/spaday/app.py   # -> http://127.0.0.1:8003
"""

import asyncio
import random
from contextlib import asynccontextmanager
from pathlib import Path

import transports
import uvicorn
from spaday import element
from starlette.applications import Starlette
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Mount, Route, WebSocketRoute
from starlette.staticfiles import StaticFiles

import daggre

HERE = Path(__file__).parent
STATIC = Path(daggre.__file__).parent / "static"  # the daggre bundle + wasm
SPADAY_DIST = HERE.parents[2] / "spaday" / "js" / "dist"  # spaday runtime (this host is a spaday app)

graph = daggre.Graph(direction="left-to-right")
graph.addNode("root", backgroundColor="lightgreen")
session = transports.Session()
session.host(graph)
server = transports.Server(session)


def shell() -> dict:
    return (
        element("div", style="font-family:system-ui;max-width:960px;margin:24px auto")
        .child(element("h1", style="font-size:18px").text("daggre inside a spaday app"))
        .child(element("p", style="color:#666;font-size:13px").text("Shell authored in spaday; the graph syncs over transports."))
        # daggre owns the <dagre-graph> element (its bundle defines it); spaday mounts it by tag
        .child(element("dagre-graph").prop("id", "graph").prop("style", "display:block;height:480px;border:1px solid #e6e6e6;border-radius:10px"))
        .to_node()
    )


async def grow(g: daggre.Graph) -> None:
    rng = random.Random(7)
    i = 0
    while True:
        await asyncio.sleep(0.8)
        if len(g.nodes) >= 18:
            continue
        i += 1
        parent = rng.choice(list(g.nodes))
        g.addNode(f"n{i}", backgroundColor="lightblue")
        g.addEdge(parent, f"n{i}", arrowhead="vee")


@asynccontextmanager
async def lifespan(app):
    tasks = [asyncio.create_task(transports.autoflush(server)), asyncio.create_task(grow(graph))]
    try:
        yield
    finally:
        for t in tasks:
            t.cancel()


app = Starlette(
    routes=[
        Route("/", lambda r: FileResponse(HERE / "app.html")),
        Route("/shell.json", lambda r: JSONResponse(shell())),
        WebSocketRoute("/ws", transports.starlette_endpoint(server)),
        Mount("/static", StaticFiles(directory=STATIC)),
        Mount("/spaday", StaticFiles(directory=SPADAY_DIST)),
    ],
    lifespan=lifespan,
)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8003)
