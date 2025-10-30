from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api import patients, admissions, wardmap

app = FastAPI(title="Triage / Admissions Platform", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(patients.router, prefix="/api")
app.include_router(admissions.router, prefix="/api")
app.include_router(wardmap.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Platformă de triere – deschide /static/index.html"}
