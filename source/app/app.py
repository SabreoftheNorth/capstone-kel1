# trigger ci

import os
import time
import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, request, g
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

REQS = Counter("http_requests_total", "Total HTTP requests", ["method", "path", "status"])
LAT = Histogram(
    "http_request_duration_seconds", "Request latency in seconds", ["method", "path"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2.5),
)


def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        dbname=os.getenv("DB_NAME", "edulearn"),
        user=os.getenv("DB_USER", "edulearn"),
        password=os.getenv("DB_PASSWORD", "changeme"),
        connect_timeout=3,
    )


def init_db():
    schema = os.path.join(os.path.dirname(__file__), "schema.sql")
    with get_conn() as conn, conn.cursor() as cur, open(schema) as f:
        cur.execute(f.read())


@app.before_request
def _start():
    g.t0 = time.time()


@app.after_request
def _record(resp):
    path = request.url_rule.rule if request.url_rule else "unknown"
    if path != "/metrics":
        REQS.labels(request.method, path, resp.status_code).inc()
        LAT.labels(request.method, path).observe(time.time() - g.t0)
    return resp


@app.get("/healthz")
def healthz():
    return jsonify(status="ok")


@app.get("/readyz")
def readyz():
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
        return jsonify(status="ready")
    except Exception:
        return jsonify(status="db-unavailable"), 503


@app.get("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@app.get("/courses")
def list_courses():
    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT id, title, description FROM courses ORDER BY id")
        return jsonify(cur.fetchall())


@app.post("/courses")
def create_course():
    d = request.get_json(force=True)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO courses(title, description) VALUES (%s,%s) RETURNING id",
                    (d["title"], d.get("description", "")))
        return jsonify(id=cur.fetchone()[0]), 201


@app.post("/students")
def create_student():
    d = request.get_json(force=True)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO students(name, email) VALUES (%s,%s) RETURNING id",
                    (d["name"], d["email"]))
        return jsonify(id=cur.fetchone()[0]), 201


@app.post("/enrollments")
def enroll():
    d = request.get_json(force=True)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO enrollments(student_id, course_id) VALUES (%s,%s) RETURNING id",
                    (d["student_id"], d["course_id"]))
        return jsonify(id=cur.fetchone()[0]), 201


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8080)
