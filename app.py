"""AutoSpec Web Application — Flask server with SSE-powered live streaming UI."""
from __future__ import annotations

import json
import os
import zipfile
import io
from datetime import datetime
from queue import Queue, Empty
from threading import Thread

from flask import Flask, render_template, request, Response, jsonify, send_file

from autospec.models import Brief, RunConfig
from autospec.demo import DEMO_BRIEF, DEFAULT_RUN_CONFIG
from autospec.orchestrator import Orchestrator

app = Flask(__name__)

# Track runs for history
run_history = []


@app.route("/")
def index():
    """Render the main AutoSpec dashboard."""
    return render_template("index.html")


@app.route("/api/run", methods=["POST"])
def start_run():
    """Start a pipeline run and stream events via SSE."""
    data = request.get_json() or {}

    brief_text = data.get("brief", "").strip()
    tech_stack = data.get("tech_stack", "Python")
    quality_threshold = data.get("quality_threshold", 90)
    demo_retry = data.get("demo_retry", False)

    # Use demo brief if no custom brief provided
    if not brief_text:
        brief = DEMO_BRIEF
        config = DEFAULT_RUN_CONFIG
    else:
        brief = Brief(text=brief_text)
        try:
            config = RunConfig(
                tech_stack_preference=tech_stack,
                quality_threshold=float(quality_threshold),
            )
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid quality threshold"}), 400

    # Create artifact dir for this run
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    artifact_dir = os.path.join(os.getcwd(), "artifacts", run_id)

    # Queue for SSE events
    event_queue: Queue = Queue()

    def emit(event_type: str, data: dict) -> None:
        event_queue.put({
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        })

    def run_pipeline():
        orch = Orchestrator(
            artifact_dir=artifact_dir,
            emit=emit,
            retry_limit=3,
            step_delay=0.6,
            demo_retry=demo_retry,
        )
        result = orch.run(brief, config)
        # Save to history
        run_history.append({
            "id": run_id,
            "brief": brief.text[:80],
            "status": result.get("status", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "artifact_dir": artifact_dir,
        })
        event_queue.put(None)

    thread = Thread(target=run_pipeline, daemon=True)
    thread.start()

    def generate():
        while True:
            try:
                event = event_queue.get(timeout=60)
                if event is None:
                    break
                yield f"data: {json.dumps(event)}\n\n"
            except Empty:
                yield f"data: {json.dumps({'type': 'keepalive', 'data': {}})}\n\n"

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.route("/api/demo-brief")
def get_demo_brief():
    return jsonify({
        "brief": DEMO_BRIEF.text,
        "tech_stack": DEFAULT_RUN_CONFIG.tech_stack_preference,
        "quality_threshold": DEFAULT_RUN_CONFIG.quality_threshold,
    })


@app.route("/api/history")
def get_history():
    return jsonify(run_history)


@app.route("/api/artifacts/<run_id>")
def download_artifacts(run_id):
    """Download all artifacts as a zip file."""
    artifact_dir = os.path.join(os.getcwd(), "artifacts", run_id)
    if not os.path.isdir(artifact_dir):
        return jsonify({"error": "Run not found"}), 404

    # Create zip in memory
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in os.listdir(artifact_dir):
            fpath = os.path.join(artifact_dir, fname)
            if os.path.isfile(fpath):
                zf.write(fpath, fname)
    mem_zip.seek(0)

    return send_file(
        mem_zip,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"autospec_artifacts_{run_id}.zip",
    )


@app.route("/api/artifacts/<run_id>/<filename>")
def view_artifact(run_id, filename):
    """View a single artifact."""
    artifact_dir = os.path.join(os.getcwd(), "artifacts", run_id)
    fpath = os.path.join(artifact_dir, filename)
    if not os.path.isfile(fpath):
        return jsonify({"error": "File not found"}), 404
    with open(fpath, "r") as f:
        content = f.read()
    return jsonify({"filename": filename, "content": content})


if __name__ == "__main__":
    print("\n⚡ AutoSpec Web UI → http://127.0.0.1:5000\n")
    app.run(debug=False, port=5000, threaded=True)
