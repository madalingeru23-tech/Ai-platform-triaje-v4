from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from app.api import auth
from app.api import triage, admissions, wardmap, discharge, pdf_export, uploads

# 🔹 Inițializăm aplicația FastAPI
app = FastAPI(title="Platformă de triaj", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Montăm fișierele statice
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# 🔹 Înregistrăm rutele API
app.include_router(triage.router, prefix="/api")
app.include_router(admissions.router, prefix="/api")
app.include_router(wardmap.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(discharge.router,  prefix="/api")
app.include_router(pdf_export.router, prefix="/api")
app.include_router(uploads.router, prefix="/api")

# 🔹 Redirecționare către triaj
@app.get("/")
def redirect_to_login():
    return RedirectResponse(url="/static/login.html")

