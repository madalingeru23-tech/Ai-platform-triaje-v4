from fastapi import APIRouter, UploadFile, File, HTTPException
import os
from uuid import uuid4

router = APIRouter()

# Directorul unde salvăm PDF-urile încărcate
UPLOAD_DIR = "triage_platform_v3_standard/uploads_investigatii"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/investigatie")
async def upload_investigatie(file: UploadFile = File(...)):
    # Acceptăm doar PDF
    ext = os.path.splitext(file.filename)[1].lower()
    if ext != ".pdf":
        raise HTTPException(status_code=400, detail="Doar fișiere PDF sunt acceptate.")

    # generăm un nume sigur: inv_<uuid>.pdf
    stored_name = f"inv_{uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, stored_name)

    # scriem PDF-ul pe disc
    with open(path, "wb") as f:
        f.write(await file.read())

    return {
        "original_name": file.filename,
        "stored_name": stored_name
    }
