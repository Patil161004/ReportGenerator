"""Report layouts (taken from CBC_FORMAT.docx and LFT_KFT_FORMAT.docx).

Row types
  test    -> name / unit / default normal range (id is used as the form field key)
  section -> bold sub-heading (e.g. "RBC INDICES")
  gap     -> blank vertical space (h = multiples of a row height)

Units may contain <sup>..</sup> / <sub>..</sub> tags.
"""


def T(id_, name, unit, rng):
    return {"type": "test", "id": id_, "name": name, "unit": unit, "range": rng}


def S(title):
    return {"type": "section", "title": title}


def G(h=1.0):
    return {"type": "gap", "h": h}


REPORTS = {
    "cbc": {
        "label": "CBC",
        "subtitle": "Complete Blood Count",
        "page": "letter",          # as in CBC_FORMAT.docx
        "row_h": 17.5,             # points
        "align": "center",         # unit / range columns centred (as in template)
        "indent": 0.0,
        "rows": [
            T("rbc", "RBC", "10<super>6</super>/mm<super>3</super>", "5.5–8.5"),
            T("hb", "Haemoglobin", "g/dl", "12–18"),
            T("pcv", "PCV", "%", "37-55"),
            T("rdw", "RDW", "%", "12-17"),
            S("RBC INDICES"),
            T("mcv", "MCV", "µm<super>3</super>", "60-72"),
            T("mch", "MCH", "Pg", "19.5-25.5"),
            T("mchc", "MCHC", "g/dl", "32-38"),
            G(1.0),
            T("wbc", "Total WBC", "10<super>3</super>/mm<super>3</super>", "6-17"),
            S("DIFFERENTIAL COUNT"),
            T("lymph", "Lymphocytes", "%", "12-30"),
            T("mono", "Monocytes", "%", "3-10"),
            T("gran", "Granulocytes", "%", "62-87"),
            T("eos", "Eosinophils", "%", "2-10"),
            G(1.0),
            T("plt", "PLATELETS", "10<super>3</super>/mm<super>3</super>", "200-500"),
            T("mpv", "MPV", "µm<super>3</super>", "5.5-10.5"),
        ],
    },
    "lft_kft": {
        "label": "LFT-KFT",
        "subtitle": "Liver & Kidney Function Test",
        "page": "a4",              # as in LFT_KFT_FORMAT.docx
        "row_h": 20.5,
        "align": "left",
        "indent": 0.3,             # inches
        "rows": [
            S("LIVER FUNCTION TEST"),
            T("alt", "SGPT/ALT", "IU/l", "10-60"),
            T("ast", "SGOT/AST", "IU/l", "10-60"),
            T("tp", "Total Proteins", "gm/dl", "5 - 8"),
            T("alb", "Albumin", "gm/dl", "3 - 4.5"),
            T("tbil", "Total Bilirubin", "mg/dl", "0.1 - 0.6"),
            T("dbil", "Direct Bilirubin", "mg/dl", "0 - 0.1"),
            G(1.6),
            S("KIDNEY FUNCTION TEST"),
            T("creat", "Serum Creatinine", "mg/dl", "0.8 - 2"),
            T("urea", "Urea", "mg/dl", "21-64"),
            T("bun", "BUN", "mg/dl", "10 – 30"),
        ],
    },
}


def public_defs():
    """Config sent to the browser (units use <sup> for HTML)."""
    out = {}
    for key, r in REPORTS.items():
        rows = []
        for row in r["rows"]:
            row = dict(row)
            if "unit" in row:
                row["unit_html"] = row["unit"].replace("<super>", "<sup>").replace("</super>", "</sup>")
            rows.append(row)
        out[key] = {"label": r["label"], "subtitle": r["subtitle"], "rows": rows}
    return out
