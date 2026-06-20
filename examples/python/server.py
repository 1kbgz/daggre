"""Serve a live daggre Graph in the browser over transports — a vanilla Starlette/uvicorn app.

    python examples/python/server.py     # -> http://127.0.0.1:8000

The graph is plain Python (`daggre.Graph`); `daggre.serve` hosts it over transports and serves the
frontend. The `grow` task mutates the graph over time and every browser updates live.
"""

import asyncio
import random

import uvicorn

import daggre


def build_graph() -> daggre.Graph:
    g = daggre.Graph(direction="left-to-right")
    g.addNode("root", backgroundColor="lightgreen")
    return g


async def grow(g: daggre.Graph) -> None:
    rng = random.Random(7)
    i = 0
    while True:
        await asyncio.sleep(0.8)
        if len(g.nodes) >= 24:
            # recolor an existing node to show live in-place updates
            g.addNode(rng.choice(list(g.nodes)), color=rng.choice(["red", "blue", "green", "orange"]))
            continue
        i += 1
        parent = rng.choice(list(g.nodes))
        g.addNode(f"n{i}", backgroundColor="lightblue")
        g.addEdge(parent, f"n{i}", arrowhead="vee", line="dash" if i % 3 == 0 else "solid")


if __name__ == "__main__":
    app = daggre.serve(build_graph(), title="daggre — live graph", background=grow)
    uvicorn.run(app, host="127.0.0.1", port=8000)
