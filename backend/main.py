import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config import TEMP_DIR, OUTPUT_DIR
from backend.routes.clip import router as clip_router
from backend.routes.caption import router as caption_router
from backend.routes.render import router as render_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.getLogger("clipcuy").info("ClipCuy starting")
    yield
    logging.getLogger("clipcuy").info("ClipCuy shutting down")

app = FastAPI(title="ClipCuy", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import FileResponse

# ... (rest of imports)

# ... (cors middleware)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend" / "out"

app.mount("/temp", StaticFiles(directory=str(TEMP_DIR)), name="temp")
app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")

app.include_router(clip_router, prefix="/api/clip", tags=["clip"])
app.include_router(caption_router, prefix="/api/caption", tags=["caption"])
app.include_router(render_router, prefix="/api/render", tags=["render"])

if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
    
    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"detail": "Not Found"}
else:
    @app.get("/")
    async def root():
        return {"message": "Frontend not found. Please build the frontend."}

