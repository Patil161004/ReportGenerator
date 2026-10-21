# Lab Report Generator (CBC / LFT-KFT)

Flask web app that fills in the MVC Parel report formats and produces a PDF.

## Run
```bash
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Use
1. Choose the report type (CBC or LFT-KFT)
2. Fill in patient details and results
3. Type the file name, then **Download PDF** (or **Preview** first)

Values outside the normal range are printed in bold automatically (switch off with the checkbox).
Normal ranges are editable per report (e.g. for cats).

## Files
- `app.py` – Flask routes
- `report_defs.py` – tests, units, normal ranges for each report (edit here to add tests / reports)
- `pdf_builder.py` – draws the PDF to match the Word templates
- `static/img` – letterhead images and signature; `fonts/` – Carlito (Calibri-compatible, OFL)
