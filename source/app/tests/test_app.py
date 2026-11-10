import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app  # noqa: E402


def test_healthz():
    r = app.test_client().get("/healthz")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_metrics():
    assert app.test_client().get("/metrics").status_code == 200
