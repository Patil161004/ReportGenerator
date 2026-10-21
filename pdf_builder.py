"""Draws the report PDF so that it matches the Word templates."""
import io
import os
import re
from datetime import datetime

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from report_defs import REPORTS

BASE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(BASE, "static", "img")
FONT_DIR = os.path.join(BASE, "fonts")

# ---- fonts (Carlito = metric-compatible with Calibri) -----------------------
REG, BOLD = "Helvetica", "Helvetica-Bold"
try:
    pdfmetrics.registerFont(TTFont("Carlito", os.path.join(FONT_DIR, "Carlito-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Carlito-Bold", os.path.join(FONT_DIR, "Carlito-Bold.ttf")))
    REG, BOLD = "Carlito", "Carlito-Bold"
except Exception:  # pragma: no cover
    pass

GREY = (0.45, 0.45, 0.45)
BLACK = (0, 0, 0)


# ---- helpers ----------------------------------------------------------------
_TAG = re.compile(r"(<super>.*?</super>|<sub>.*?</sub>)")


def _segments(text):
    for part in _TAG.split(text):
        if not part:
            continue
        if part.startswith("<super>"):
            yield part[7:-8], "sup"
        elif part.startswith("<sub>"):
            yield part[5:-6], "sub"
        else:
            yield part, "n"


def rich_width(text, font, size):
    w = 0
    for t, k in _segments(text):
        w += pdfmetrics.stringWidth(t, font, size * (0.62 if k != "n" else 1))
    return w


def draw_rich(c, x, y, text, font, size, align="left"):
    """Draw text with <super>/<sub> support. align: left | center | right."""
    w = rich_width(text, font, size)
    if align == "center":
        x -= w / 2
    elif align == "right":
        x -= w
    for t, k in _segments(text):
        s = size * (0.62 if k != "n" else 1)
        dy = size * 0.38 if k == "sup" else (-size * 0.12 if k == "sub" else 0)
        c.setFont(font, s)
        c.drawString(x, y + dy, t)
        x += pdfmetrics.stringWidth(t, font, s)


def fit_size(text, font, size, max_w, min_size=6.0):
    while size > min_size and pdfmetrics.stringWidth(text, font, size) > max_w:
        size -= 0.25
    return size


def fmt_date(s):
    """Accepts yyyy-mm-dd (from <input type=date>) or anything else -> dd/mm/yyyy."""
    s = (s or "").strip()
    try:
        return datetime.strptime(s, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return s


_RANGE = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*[-–—]\s*(-?\d+(?:\.\d+)?)\s*$")


def is_abnormal(value, rng):
    """True when numeric value lies outside a 'lo-hi' range."""
    try:
        v = float(str(value).strip().replace(",", "."))
    except ValueError:
        return False
    m = _RANGE.match(rng or "")
    if not m:
        return False
    lo, hi = float(m.group(1)), float(m.group(2))
    return v < lo or v > hi


# ---- main -------------------------------------------------------------------
def build_pdf(report_key, form):
    rd = REPORTS[report_key]
    pagesize = letter if rd["page"] == "letter" else A4
    W, H = pagesize
    Win, Hin = W / inch, H / inch

    pat = form.get("patient", {})
    results = form.get("results", {})
    auto_flag = bool(form.get("flag", True))
    show_sig = bool(form.get("signature", True))

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=pagesize)
    c.setTitle(f"{rd['label']} Report - {pat.get('patient', '')}".strip(" -"))
    c.setAuthor("Department of Veterinary Physiology, Mumbai Veterinary College")

    def Y(top_in):               # inches from top of page -> pdf y (points)
        return H - top_in * inch

    def image(name, x_in, top_in, w_in, h_in):
        c.drawImage(os.path.join(IMG, name), x_in * inch, Y(top_in + h_in),
                    w_in * inch, h_in * inch, mask="auto")

    L = 1.2                       # content left (in)
    R = Win - 1.2                 # content right (in)

    # ---------- letterhead ----------
    cx = Win / 2 + 0.1
    ex = cx - 0.249
    image("animals_big.jpeg", 0.15, 0.15, 2.4, 0.4375)
    image("animals_big.jpeg", Win - 0.2 - 2.417, 0.15, 2.417, 0.4375)
    image("emblem.png", ex, 0.15, 0.498, 0.74)
    image("animals_small.png", ex - 1.433, 0.333, 0.698, 0.25)
    image("animals_small.png", ex + 1.233, 0.385, 0.552, 0.198)

    c.setFillColorRGB(*GREY)
    c.setFont(REG, 8)
    c.drawRightString((Win - 0.55) * inch, Y(0.80), ": 022 241370 30 / 1180; Ext: 125")
    c.setFillColorRGB(*BLACK)

    c.setFont(BOLD, 14)
    c.drawCentredString(W / 2, Y(1.26), "Department of Veterinary Physiology")
    t2 = "Mumbai Veterinary College, Parel, Mumbai"
    s2 = fit_size(t2, BOLD, 20, (Win - 1.0) * inch)
    c.setFont(BOLD, s2)
    c.drawCentredString(W / 2, Y(1.62), t2)
    c.setFont(BOLD, 11)
    c.drawCentredString(W / 2, Y(1.92), "(Maharashtra Animal and Fishery Sciences University, Nagpur)")

    c.setLineWidth(1.8)
    c.line((L - 0.1) * inch, Y(2.03), (R + 0.1) * inch, Y(2.03))
    c.setLineWidth(0.5)
    c.line((L - 0.1) * inch, Y(2.075), (R + 0.1) * inch, Y(2.075))

    # ---------- patient block ----------
    age = (pat.get("age") or "").strip()
    sex = (pat.get("sex") or "").strip()
    age_sex = "/".join(p for p in (age, sex) if p)
    left_rows = [
        ("Owner’s Name", pat.get("owner", "")),
        ("Patient’s Name", pat.get("patient", "")),
        ("Age/Sex", age_sex),
        ("Species/Breed", pat.get("species", "")),
        ("Ref", pat.get("ref", "")),
    ]
    right_rows = [
        ("Ref. No.", pat.get("ref_no", "")),
        ("Collected", fmt_date(pat.get("collected"))),
        ("Received", fmt_date(pat.get("received"))),
        ("Reported", fmt_date(pat.get("reported"))),
    ]
    top = 2.42
    step = 0.205
    rx = L + 3.75
    for i, (lab, val) in enumerate(left_rows):
        y = Y(top + i * step)
        c.setFont(REG, 10)
        c.drawString(L * inch, y, lab)
        c.drawString((L + 1.05) * inch, y, ":")
        val = str(val)
        c.setFont(REG, fit_size(val, REG, 10, (rx - L - 1.2 - 0.15) * inch))
        c.drawString((L + 1.2) * inch, y, val)
    for i, (lab, val) in enumerate(right_rows):
        y = Y(top + i * step)
        c.setFont(REG, 10)
        c.drawString(rx * inch, y, lab)
        c.drawString((rx + 0.85) * inch, y, ":")
        val = str(val)
        c.setFont(REG, fit_size(val, REG, 10, (R - rx - 1.0) * inch))
        c.drawString((rx + 1.0) * inch, y, val)
    c.setLineWidth(0.7)
    c.line(L * inch, Y(3.42), R * inch, Y(3.42))

    # ---------- results table ----------
    centre = rd["align"] == "center"
    if centre:
        x_res, x_unit, x_rng = L + 1.95, L + 3.72, L + 5.03
    else:
        x_res, x_unit, x_rng = L + 1.93, L + 3.30, L + 4.55
    al = "center" if centre else "left"

    hy = Y(3.98)
    c.setFont(BOLD, 11)
    c.drawString(L * inch, hy, "Test")
    c.drawString(x_res * inch, hy, "Result")
    draw_rich(c, x_unit * inch, hy, "Units", BOLD, 11, al)
    draw_rich(c, x_rng * inch, hy, "Normal Range", BOLD, 11, al)

    y = Y(4.38)
    row_h = rd["row_h"]
    indent = rd["indent"]
    for row in rd["rows"]:
        kind = row["type"]
        if kind == "gap":
            y -= row_h * row["h"]
            continue
        if kind == "section":
            c.setFont(BOLD, 9.5)
            c.drawString((L + (indent - 0.1 if indent else 0)) * inch, y, row["title"])
            y -= row_h
            continue
        entry = results.get(row["id"], {}) or {}
        val = str(entry.get("value", "") or "").strip()
        rng = str(entry.get("range", row["range"]) or "").strip()
        bold = auto_flag and is_abnormal(val, rng)

        c.setFont(REG, 10)
        c.drawString((L + indent) * inch, y, row["name"])
        c.setFont(BOLD if bold else REG, 10)
        c.drawString(x_res * inch, y, val)
        draw_rich(c, x_unit * inch, y, row["unit"], REG, 10, al)
        draw_rich(c, x_rng * inch, y, rng, REG, 10, al)
        y -= row_h

    # ---------- signature ----------
    end_in = (H - y) / inch
    sig_top = max(end_in + 0.25, 8.0)
    if show_sig:
        image("signature.jpeg", R - 1.55, sig_top, 1.0, 0.325)
    c.setFont(REG, 10)
    c.drawRightString(R * inch, Y(sig_top + 0.325 + 0.42), "Checked/Verified")

    # ---------- footer ----------
    c.setFillColorRGB(*GREY)
    c.setFont(BOLD, 7)
    c.drawString(L * inch, 0.6 * inch, "Results relate only to the sample as received")
    c.drawRightString(R * inch, 0.6 * inch, "Results to be correlated with the clinical signs")

    c.showPage()
    c.save()
    return buf.getvalue()
