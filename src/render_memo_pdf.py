"""
Executive Memo PDF Generator.
Converts outputs/executive_memo.md into a publication-grade PDF via headless browser.
"""
import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MEMO_MD = BASE_DIR / "outputs" / "executive_memo.md"
MEMO_HTML = BASE_DIR / "outputs" / "executive_memo_print.html"
MEMO_PDF = BASE_DIR / "outputs" / "executive_memo.pdf"


def get_browser_path():
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    raise FileNotFoundError("Neither Microsoft Edge nor Google Chrome found for PDF rendering.")


def md_to_html(md_text: str) -> str:
    # A lightweight, elegant markdown-to-html converter tailored for executive memos
    html_lines = []
    in_table = False
    table_lines = []

    def flush_table():
        nonlocal in_table, table_lines
        if not table_lines:
            return
        out = ["<table>"]
        # Header
        header_cols = [c.strip() for c in table_lines[0].split("|")[1:-1]]
        out.append("<thead><tr>" + "".join(f"<th>{c}</th>" for c in header_cols) + "</tr></thead>")
        out.append("<tbody>")
        for row in table_lines[2:]: # skip separator
            cols = [c.strip() for c in row.split("|")[1:-1]]
            out.append("<tr>" + "".join(f"<td>{c}</td>" for c in cols) + "</tr>")
        out.append("</tbody></table>")
        html_lines.append("\n".join(out))
        table_lines = []
        in_table = False

    lines = md_text.splitlines()
    for line in lines:
        sline = line.strip()
        if sline.startswith("|") and sline.endswith("|"):
            in_table = True
            table_lines.append(sline)
            continue
        elif in_table:
            flush_table()

        if sline.startswith("# "):
            html_lines.append(f"<h1>{sline[2:]}</h1>")
        elif sline.startswith("### "):
            html_lines.append(f"<h3>{sline[4:]}</h3>")
        elif sline.startswith("## "):
            html_lines.append(f"<h2>{sline[3:]}</h2>")
        elif sline.startswith("---"):
            html_lines.append("<hr>")
        elif sline.startswith("- "):
            html_lines.append(f"<li>{sline[2:]}</li>")
        elif sline.startswith("1. ") or sline.startswith("2. ") or sline.startswith("3. ") or sline.startswith("4. ") or sline.startswith("5. "):
            html_lines.append(f"<li class='num-item'>{sline[3:]}</li>")
        elif sline == "":
            html_lines.append("<div style='height: 6px;'></div>")
        else:
            html_lines.append(f"<p>{sline}</p>")

    if in_table:
        flush_table()

    body_content = "\n".join(html_lines)
    # Inline formatting: bold, italics, code, math
    import re
    body_content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", body_content)
    body_content = re.sub(r"\*(.+?)\*", r"<em>\1</em>", body_content)
    body_content = re.sub(r"`(.+?)`", r"<code>\1</code>", body_content)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {{
    size: A4;
    margin: 12mm 14mm 12mm 14mm;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #0f172a;
    font-size: 9.5pt;
    line-height: 1.42;
    background: #fff;
  }}
  h1 {{
    font-size: 16pt;
    font-weight: 800;
    color: #0f172a;
    margin: 0 0 8px 0;
    letter-spacing: -0.3px;
    border-bottom: 2px solid #0284c7;
    padding-bottom: 4px;
  }}
  h2 {{
    font-size: 12pt;
    font-weight: 700;
    color: #0284c7;
    margin: 10px 0 4px 0;
  }}
  h3 {{
    font-size: 10.5pt;
    font-weight: 700;
    color: #0369a1;
    margin: 9px 0 3px 0;
    border-left: 3px solid #0284c7;
    padding-left: 6px;
  }}
  p {{
    margin: 0 0 5px 0;
  }}
  hr {{
    border: none;
    border-top: 1px solid #cbd5e1;
    margin: 8px 0;
  }}
  ul, ol {{
    margin: 2px 0 6px 16px;
    padding: 0;
  }}
  li {{
    margin-bottom: 3px;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 6px 0 8px 0;
    font-size: 8pt;
    line-height: 1.25;
  }}
  th {{
    background-color: #f1f5f9;
    color: #334155;
    font-weight: 700;
    text-align: left;
    padding: 4px 6px;
    border: 1px solid #cbd5e1;
  }}
  td {{
    padding: 4px 6px;
    border: 1px solid #e2e8f0;
    vertical-align: top;
  }}
  tr:nth-child(even) td {{
    background-color: #f8fafc;
  }}
  code {{
    font-family: Consolas, Monaco, monospace;
    font-size: 8.5pt;
    background: #f1f5f9;
    padding: 1px 3px;
    border-radius: 3px;
    color: #0f172a;
  }}
  strong {{
    font-weight: 700;
    color: #0f172a;
  }}
  .header-meta {{
    font-size: 9pt;
    color: #334155;
    margin-bottom: 8px;
    line-height: 1.35;
  }}
</style>
</head>
<body>
{body_content}
</body>
</html>"""


def generate_pdf():
    print(f"1. Reading {MEMO_MD}...")
    with open(MEMO_MD, "r", encoding="utf-8") as f:
        md_text = f.read()

    print("2. Generating HTML print template...")
    html_content = md_to_html(md_text)
    with open(MEMO_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    browser = get_browser_path()
    print(f"3. Rendering PDF using {Path(browser).name}...")

    cmd = [
        browser,
        "--headless",
        "--disable-gpu",
        "--allow-file-access-from-files",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={MEMO_PDF}",
        f"file:///{str(MEMO_HTML).replace(os.sep, '/')}",
    ]

    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if MEMO_PDF.exists() and MEMO_PDF.stat().st_size > 0:
        print(f"SUCCESS: Created {MEMO_PDF} ({MEMO_PDF.stat().st_size} bytes)")
    else:
        raise RuntimeError("PDF generation failed: output file is empty or missing.")


if __name__ == "__main__":
    generate_pdf()
