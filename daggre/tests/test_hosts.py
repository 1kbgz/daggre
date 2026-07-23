import asyncio
import json

from starlette.applications import Starlette
from starlette.testclient import TestClient

import daggre


def test_lazy_host_adapters_are_exposed():
    # serve / Widget are imported lazily via module __getattr__
    assert callable(daggre.serve)
    assert daggre.Widget is not None


def test_serve_builds_an_app_and_serves_the_page():
    g = daggre.Graph(direction="left-to-right")
    g.addNode("a", color="red")

    async def bg(graph):
        await asyncio.sleep(0)

    app = daggre.serve(g, title="demo graph", background=bg)
    assert isinstance(app, Starlette)
    with TestClient(app) as client:  # runs the lifespan (autosync + background)
        resp = client.get("/")
        assert resp.status_code == 200
        assert "demo graph" in resp.text


def test_widget_streams_snapshot_then_patch():
    g = daggre.Graph(direction="left-to-right")
    g.addNode("a", color="red")
    g.addEdge("a", "b", line="dash")

    w = daggre.Widget(g)
    sent = []
    w.send = lambda content, buffers=None: sent.append(content)  # capture outbound comm msgs

    w._on_msg(w, {"ready": True}, [])  # frontend signals ready -> opening snapshot
    assert json.loads(sent[0]["wire"])["t"] == "snapshot"

    g.addNode("c")  # mutate after open
    w.flush()
    assert json.loads(sent[-1]["wire"])["t"] == "patch"

    # an inbound {wire} message is relayed to the server (a non-patch is a no-op)
    n_before = len(sent)
    w._on_msg(w, {"wire": sent[0]["wire"]}, [])
    assert len(sent) == n_before

    # non-dict / unrelated messages are ignored
    w._on_msg(w, "not-a-dict", [])
    w._on_msg(w, {"other": 1}, [])
