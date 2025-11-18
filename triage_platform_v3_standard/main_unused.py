from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from triage_platform_v3_standard.app.api import triage, admissions

app = FastAPI(title="Platformă de triaj", version="1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servește fișierele statice
app.mount("/static", StaticFiles(directory="triage_platform_v3_standard/static"), name="static")

# Include rutele API
app.include_router(triage.router, prefix="/api")
app.include_router(admissions.router, prefix="/api")

# Redirect către pagina principală
@app.get("/")
def redirect_to_triaj():
    return RedirectResponse(url="/static/triaj.html")
