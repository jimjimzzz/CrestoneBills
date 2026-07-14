#!/usr/bin/env python3
"""Regenerates index.html from bills.json. Run after editing bills.json."""
import json

DATA_PATH = "bills.json"
OUT_PATH = "index.html"

DEFAULT_LABEL = {
    "paid": "Paid",
    "unpaid": "Unpaid",
    "coming-soon": "Coming Soon",
}
AMOUNT_STATUSES = {"unpaid", "due-later", "overdue"}

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{title} — Bills</title>
<link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet"/>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'DM Sans', sans-serif; background: #f7f6f3; color: #1a1a1a; min-height: 100vh; padding-bottom: 80px; }}
.page-header {{ background: #1a1a1a; color: #fff; padding: 44px 56px 40px; }}
.page-header h1 {{ font-family: 'Libre Baskerville', serif; font-size: 2rem; font-weight: 400; line-height: 1.2; letter-spacing: -0.01em; }}
.page-header h1 em {{ font-style: italic; opacity: 0.55; }}
.page-header-meta {{ display: flex; gap: 40px; margin-top: 20px; flex-wrap: wrap; }}
.meta {{ font-size: 0.75rem; color: rgba(255,255,255,0.45); font-weight: 400; letter-spacing: 0.05em; text-transform: uppercase; }}
.meta strong {{ display: block; font-size: 0.88rem; color: rgba(255,255,255,0.85); font-weight: 500; letter-spacing: 0; text-transform: none; margin-top: 3px; }}
.content {{ max-width: 1060px; margin: 0 auto; padding: 40px 24px 0; }}
.month-section {{ margin-bottom: 40px; }}
.month-label {{ font-family: 'Libre Baskerville', serif; font-size: 1.1rem; font-weight: 400; color: #1a1a1a; margin-bottom: 12px; }}
.month-label em {{ font-style: italic; }}
.bill-table {{ width: 100%; table-layout: fixed; background: #fff; border-radius: 10px; border: 1px solid #e4e2dd; overflow: hidden; border-collapse: collapse; }}
.bill-table thead tr {{ background: #f2f1ee; border-bottom: 1px solid #e4e2dd; }}
.bill-table th {{ padding: 10px 12px; font-size: 0.65rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #aaa; text-align: left; }}
.bill-table th:nth-child(1), .bill-table td:nth-child(1) {{ width: 34%; }}
.bill-table th:nth-child(2), .bill-table td:nth-child(2) {{ width: 32%; }}
.bill-table th:nth-child(3), .bill-table td:nth-child(3) {{ width: 12%; }}
.bill-table th:nth-child(4), .bill-table td:nth-child(4) {{ width: 22%; padding-right: 28px; }}
.bill-table td {{ padding: 15px 12px; font-size: 0.85rem; border-top: 1px solid #f0eeea; vertical-align: middle; }}
.bill-table tr:first-child td {{ border-top: none; }}
.bill-table tbody tr:not(.unpaid-total-row):hover {{ background: #faf9f7; }}
.util-cell {{ display: flex; align-items: center; gap: 10px; }}
.util-icon {{ font-size: 1rem; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; border-radius: 8px; flex-shrink: 0; }}
.util-name {{ font-weight: 500; font-size: 0.87rem; }}
.util-provider {{ font-size: 0.72rem; color: #aaa; margin-top: 1px; }}
.amount {{ font-weight: 600; font-size: 0.92rem; }}
.period {{ font-size: 0.78rem; color: #888; }}
.status {{ display: inline-flex; align-items: center; gap: 5px; padding: 4px 11px; border-radius: 100px; font-size: 0.68rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; white-space: nowrap; }}
.status::before {{ content: ''; width: 5px; height: 5px; border-radius: 50%; background: currentColor; }}
.unpaid      {{ background: #fef2f2; color: #c0392b; }}
.paid        {{ background: #f0faf5; color: #27ae60; }}
.coming-soon {{ background: #fdf6ec; color: #b07d2a; }}
.due-later   {{ background: #eef4fb; color: #2a6fa3; }}
.due-note {{ font-size: 0.67rem; color: #c0392b; margin-left: 6px; white-space: nowrap; font-weight: 700; }}
.pay-note {{ font-size: 0.67rem; color: #27ae60; margin-left: 6px; white-space: nowrap; }}
.unpaid-total-row td {{ background: #fef9f9; border-top: 1px solid #f5e0e0 !important; }}
.unpaid-label {{ font-size: 0.72rem; font-weight: 600; color: #c0392b; letter-spacing: 0.04em; text-transform: uppercase; }}
.unpaid-amount {{ font-weight: 700; font-size: 0.95rem; color: #c0392b; }}
.footer {{ text-align: center; margin-top: 60px; font-size: 0.72rem; color: #bbb; padding: 0 24px; }}
@media (max-width: 640px) {{
  .page-header {{ padding: 32px 24px 28px; }}
  .bill-table th:nth-child(2), .bill-table td:nth-child(2) {{ display: none; }}
}}
</style>
</head>
<body>
<div class="page-header">
  <h1>{title} <em>· {location}</em></h1>
  <div class="page-header-meta">
    <div class="meta">Tenant<strong>{tenant}</strong></div>
    <div class="meta">Monthly Rent<strong>{monthly_rent}</strong></div>
    <div class="meta">Property<strong>{zip_line}</strong></div>
  </div>
</div>
<div class="content">
"""

FOOT = """</div>
<div class="footer">{title} · {zip_line} · {updated}</div>
</body>
</html>"""


def status_label(row):
    if row.get("label"):
        return row["label"]
    return DEFAULT_LABEL.get(row["status"], row["status"])


def money_to_float(amount):
    if not amount or amount == "—":
        return 0.0
    return float(amount.replace("$", "").replace(",", ""))


def render_row(row, headers):
    icon_bg = "#f0f0f0"
    label = status_label(row)
    note_html = f'<span class="{"pay-note" if row["status"] == "paid" else "due-note"}">{row["note"]}</span>' if row.get("note") else ""
    amount_html = row["amount"] if row["amount"] else "—"
    return f'''        <tr>
          <td><div class="util-cell"><div class="util-icon" style="background:{icon_bg}">{row["icon"]}</div><div><div class="util-name">{row["utility"]}</div><div class="util-provider">{row["provider"]}</div></div></div></td>
          <td><span class="period">{row["period"]}</span></td>
          <td><span class="amount">{amount_html}</span></td>
          <td><span class="status {row["status"]}">{label}</span>{note_html}</td>
        </tr>'''


def render_section(sec):
    if sec["type"] == "propane":
        title_html = f'<em>{sec["title"]} <span style="opacity:0.55">· {sec["subtitle"]}</span></em>'
        headers = ["Type", "Date", "Amount", "Status"]
    else:
        title_html = f'<em>{sec["title"]}</em>'
        headers = ["Utility", "Service Period", "Amount", "Status"]

    rows_html = "\n".join(render_row(r, headers) for r in sec["rows"])

    total = sum(money_to_float(r["amount"]) for r in sec["rows"] if r["status"] in AMOUNT_STATUSES)
    total_row = ""
    if total > 0:
        total_row = f'''
        <tr class="unpaid-total-row">
          <td colspan="2" class="unpaid-label">{sec["unpaid_label"]}</td>
          <td class="unpaid-amount">${total:,.2f}</td>
          <td></td>
        </tr>'''

    header_cells = "".join(f"<th>{h}</th>" for h in headers)

    return f'''  <div class="month-section">
    <div class="month-label">{title_html}</div>
    <table class="bill-table">
      <thead><tr>
        {header_cells}
      </tr></thead>
      <tbody>
{rows_html}{total_row}
      </tbody>
    </table>
  </div>
'''


def build():
    data = json.load(open(DATA_PATH, encoding="utf-8"))
    prop = data["property"]
    html = HEAD.format(**prop)
    html += "\n".join(render_section(sec) for sec in data["sections"])
    html += FOOT.format(title=prop["title"], zip_line=prop["zip_line"], updated=data["updated"])
    open(OUT_PATH, "w", encoding="utf-8").write(html)
    print(f"Wrote {OUT_PATH} ({len(html):,} bytes)")


if __name__ == "__main__":
    build()
