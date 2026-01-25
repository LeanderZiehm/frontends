from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import urllib.parse

app = FastAPI()

BASE_DIR = Path(__file__).parent
ALLOWED_EXTENSIONS = {".html", ".css", ".js"}  # allow CSS/JS for static serving

class FilteredStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        # Ensure self.directory is a Path object
        base_dir = Path(self.directory) if self.directory is not None else Path(".")
        full_path = (base_dir / path).resolve()
        
        if not full_path.exists() or full_path.suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=404, detail="File not found")
        return await super().get_response(path, scope)

app.mount("/static", FilteredStaticFiles(directory=BASE_DIR), name="static")

def build_index_html() -> str:
    """Generate a modern-looking HTML index showing .html files."""

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Frontend Index</title>
        <style>
            /* Reset some basic styles */
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
                border-radius: 12px;
                padding: 40px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                width: 100%;
                max-width: 700px;
            }

            h1 {
                text-align: center;
                margin-bottom: 30px;
                color: #333;
                font-size: 2.5rem;
            }

            ul {
                list-style: none;
            }

            li {
                margin: 12px 0;
            }

            a {
                text-decoration: none;
                padding: 12px 20px;
                display: block;
                border-radius: 8px;
                background: #4f46e5;
                color: white;
                font-weight: 600;
                transition: all 0.3s ease;
            }

            a:hover {
                background: #6366f1;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }

            .subpath {
                font-size: 0.9rem;
                color: #555;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Frontend Index</h1>
            <ul>
    """

    seen_folders = set()
    for file_path in BASE_DIR.rglob("*.html"):
        rel_path = file_path.relative_to(BASE_DIR)

        if rel_path.name == "index.html":
            folder = rel_path.parent
            display_name = "Home" if folder == Path('.') else folder.name
            if folder not in seen_folders:
                url_path = "/static/" + urllib.parse.quote(str(rel_path))
                html += f'<li><a href="{url_path}">{display_name}</a></li>'
                seen_folders.add(folder)
        else:
            url_path = "/static/" + urllib.parse.quote(str(rel_path))
            html += f'<li><a href="{url_path}">{rel_path}</a></li>'

    html += """
            </ul>
        </div>
    </body>
    </html>
    """

    return html

@app.get("/", response_class=HTMLResponse)
async def index():
    return build_index_html()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)
