from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import PROJECT_ROOT
from app.routes.chat import router as chat_router

app = FastAPI()
app.include_router(chat_router)

_APP_DIR = PROJECT_ROOT / "app"
TEMPLATES_DIR = _APP_DIR / "templates"
STATIC_DIR = _APP_DIR / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return FileResponse(str(TEMPLATES_DIR / "index.html"))

