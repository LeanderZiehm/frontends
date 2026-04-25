from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import urllib.parse

app = FastAPI()

BASE_DIR = Path(__file__).parent

ALLOWED_EXTENSIONS = {".html", ".css", ".js"}


# -----------------------------
# FILE SERVER (FIXED FOR VERCEL)
# -----------------------------
@app.get("/p/{path:path}")
async def serve_static(path: str):
    full_path = BASE_DIR / path

    # Case 1: folder route → /extract-colors → /extract-colors/index.html
    if full_path.is_dir():
        full_path = full_path / "index.html"

    # Case 2: no extension → assume html page
    elif full_path.suffix == "":
        full_path = full_path.with_suffix(".html")

    full_path = full_path.resolve()

    # Security + existence check
    if (
        not full_path.exists()
        or full_path.suffix not in ALLOWED_EXTENSIONS
        or BASE_DIR not in full_path.parents
    ):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(full_path)


# -----------------------------
# INDEX PAGE GENERATOR
# -----------------------------
def build_index_html() -> str:
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Frontend Index</title>

        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: Arial, sans-serif;
            }

            body {
                background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }

            .container {
                background: white;
                padding: 40px;
                border-radius: 12px;
                width: 100%;
                max-width: 700px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }

            h1 {
                text-align: center;
                margin-bottom: 25px;
            }

            a {
                display: block;
                padding: 12px;
                margin: 8px 0;
                background: #4f46e5;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                transition: 0.2s;
            }

            a:hover {
                background: #6366f1;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Frontend Index</h1>
            <ul>
    """

    seen = set()

    # find all index.html files
    for file_path in BASE_DIR.rglob("index.html"):
        rel = file_path.relative_to(BASE_DIR)
        folder = rel.parent

        # skip root index
        if folder == Path("."):
            continue

        if folder in seen:
            continue

        url = "/p/" + urllib.parse.quote(str(folder))
        html += f'<a href="{url}/">{folder}</a>\n'
        seen.add(folder)

    html += """
            </ul>
        </div>
    </body>
    </html>
    """

    return html


# -----------------------------
# ROOT
# -----------------------------
@app.get("/", response_class=HTMLResponse)
async def index():
    return build_index_html()


# -----------------------------
# OPTIONAL: health check
# -----------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}
