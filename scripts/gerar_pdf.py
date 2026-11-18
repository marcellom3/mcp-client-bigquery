"""Gera guia-mcp-bigquery.pdf a partir do README.md.

Requisitos: Python com os pacotes `markdown` e `pymdown-extensions`, e Google Chrome ou Microsoft Edge instalado.
Uso: python scripts/gerar_pdf.py
"""

import shutil
import subprocess
import tempfile
from datetime import date
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "guia-mcp-bigquery.pdf"

BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "google-chrome", "chromium", "msedge",
]

CSS = """
@page { size: A4; margin: 18mm 16mm; }
body { font-family: "Segoe UI", Arial, sans-serif; font-size: 10.5pt; line-height: 1.5; color: #1f2328; }
h1 { font-size: 20pt; border-bottom: 3px solid #1a73e8; padding-bottom: 6px; margin-top: 0; }
h2 { font-size: 14pt; color: #1a73e8; margin-top: 22px; break-after: avoid; }
h3 { font-size: 11.5pt; margin-top: 16px; break-after: avoid; }
hr { border: 0; border-top: 1px solid #d0d7de; margin: 18px 0; }
code { font-family: Consolas, "Courier New", monospace; font-size: 9pt; background: #f2f4f7; padding: 1px 4px; border-radius: 3px; }
pre { background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 6px; padding: 10px; white-space: pre-wrap; word-break: break-all; break-inside: avoid; }
pre code { background: none; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; break-inside: avoid; font-size: 9.5pt; }
th, td { border: 1px solid #d0d7de; padding: 5px 8px; text-align: left; vertical-align: top; }
th { background: #eef3fd; }
blockquote { margin: 8px 0; padding: 6px 12px; border-left: 4px solid #1a73e8; background: #f4f8ff; color: #3d4752; }
a { color: #1a73e8; text-decoration: none; }
.rodape { margin-top: 24px; font-size: 8.5pt; color: #6e7781; border-top: 1px solid #d0d7de; padding-top: 6px; }
"""


def find_browser() -> str:
    for b in BROWSERS:
        path = shutil.which(b) or (b if Path(b).is_file() else None)
        if path:
            return path
    raise SystemExit("Chrome ou Edge não encontrado.")


def main() -> None:
    body = markdown.markdown((ROOT / "README.md").read_text(encoding="utf-8"),
                             extensions=["tables", "pymdownx.superfences", "toc"])
    html = (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>MCP BigQuery - Guia do cliente</title>'
            f"<style>{CSS}</style></head><body>{body}"
            f'<div class="rodape">Versão de {date.today():%d/%m/%Y} · '
            f"github.com/marcellom3/mcp-client-bigquery</div></body></html>")
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "guia.html"
        page.write_text(html, encoding="utf-8")
        subprocess.run([find_browser(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={OUTPUT}", page.as_uri()], check=True, capture_output=True)
    print(f"PDF gerado: {OUTPUT}")


if __name__ == "__main__":
    main()
