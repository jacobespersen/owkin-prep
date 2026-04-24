from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

TEMPLATES_DIR = Path("app/templates")
STATIC_DIR = Path("app/static")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def root():
    return FileResponse(str(TEMPLATES_DIR / "index.html"))
