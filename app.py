"""Veterinary lab report generator (CBC / LFT-KFT) -> PDF.

Run:  python app.py      then open  http://127.0.0.1:5000
"""
import io
import re

from flask import Flask, jsonify, render_template, request, send_file

from pdf_builder import build_pdf
from report_defs import REPORTS, public_defs

app = Flask(__name__)


def safe_filename(name, fallback="report"):
    name = (name or "").strip()
    name = re.sub(r"\.pdf$", "", name, flags=re.I)
    name = re.sub(r"[^\w\s().-]", "", name, flags=re.UNICODE)   # drop slashes, quotes, etc.
    name = re.sub(r"\s+", "_", name).strip("._ ")
    return (name or fallback)[:100] + ".pdf"


@app.get("/")
def index():
    return render_template("index.html", defs=public_defs())


@app.post("/api/pdf")
def make_pdf():
    data = request.get_json(silent=True) or {}
    key = data.get("report")
    if key not in REPORTS:
        return jsonify(error="Unknown report type"), 400

    # only keep known result fields
    valid_ids = {r["id"] for r in REPORTS[key]["rows"] if r["type"] == "test"}
    results = {k: v for k, v in (data.get("results") or {}).items() if k in valid_ids}

    form = {
        "patient": {k: str(v)[:120] for k, v in (data.get("patient") or {}).items()},
        "results": results,
        "flag": data.get("flag", True),
        "signature": data.get("signature", True),
    }
    pdf = build_pdf(key, form)
    fname = safe_filename(data.get("filename"), fallback=f"{key}_report")
    download = request.args.get("download") == "1"
    return send_file(
        io.BytesIO(pdf),
        mimetype="application/pdf",
        as_attachment=download,
        download_name=fname,
    )


if __name__ == "__main__":
    app.run(debug=True)
