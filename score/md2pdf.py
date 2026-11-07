#!/usr/bin/env python3
"""Render a Markdown report to PDF. Usage: md2pdf.py report.md report.pdf
Markdown -> HTML (python-markdown, tables and fenced code on) -> PDF by headless Chrome when it is installed,
else by reportlab from the plain text. Images referenced with relative paths resolve against the report's folder."""
import sys, os, subprocess, tempfile, shutil, html
import markdown

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CSS = """
body{font-family:Georgia,'Times New Roman',serif;font-size:11.5pt;line-height:1.45;max-width:17cm;margin:1.8cm auto;color:#111}
h1{font-size:19pt;margin:0 0 .4em} h2{font-size:13.5pt;margin:1.2em 0 .3em} h3{font-size:12pt;margin:1em 0 .2em}
table{border-collapse:collapse;font-size:10pt;margin:.6em 0} th,td{border:1px solid #999;padding:3px 7px;text-align:left}
code,pre{font-family:Menlo,Consolas,monospace;font-size:9.5pt} pre{background:#f4f4f4;padding:8px;overflow-x:auto;white-space:pre-wrap}
img{max-width:100%} p{margin:.5em 0}
"""

def to_html(md_path):
    text = open(md_path, encoding="utf-8").read()
    body = markdown.markdown(text, extensions=["tables", "fenced_code"])
    return f"<!doctype html><meta charset='utf-8'><style>{CSS}</style><body>{body}</body>"

def chrome_pdf(html_path, pdf_path):
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
           f"--print-to-pdf={os.path.abspath(pdf_path)}", "file://" + os.path.abspath(html_path)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0

def reportlab_pdf(md_path, pdf_path):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
    styles = getSampleStyleSheet(); story = []
    for line in open(md_path, encoding="utf-8"):
        s = line.rstrip("\n")
        if s.startswith("# "): story.append(Paragraph(html.escape(s[2:]), styles["Title"]))
        elif s.startswith("## "): story.append(Paragraph(html.escape(s[3:]), styles["Heading2"]))
        elif s.startswith("### "): story.append(Paragraph(html.escape(s[4:]), styles["Heading3"]))
        elif s.strip() == "": story.append(Spacer(1, 6))
        elif s.startswith("|") or s.startswith("    ") or s.startswith("```"): story.append(Preformatted(s, styles["Code"]))
        else: story.append(Paragraph(html.escape(s), styles["BodyText"]))
    SimpleDocTemplate(pdf_path, pagesize=A4).build(story)

def main():
    md_path, pdf_path = sys.argv[1], sys.argv[2]
    folder = os.path.dirname(os.path.abspath(md_path)) or "."
    html_path = os.path.join(folder, os.path.splitext(os.path.basename(md_path))[0] + ".html")
    open(html_path, "w", encoding="utf-8").write(to_html(md_path))
    ok = False
    if os.path.exists(CHROME):
        try: ok = chrome_pdf(html_path, pdf_path)
        except Exception as e: print("chrome failed:", e, file=sys.stderr)
    if not ok:
        reportlab_pdf(md_path, pdf_path); print("rendered by reportlab (plain)", file=sys.stderr)
    else:
        print("rendered by chrome", file=sys.stderr)
    print(pdf_path, os.path.getsize(pdf_path), "bytes")

if __name__ == "__main__":
    main()
