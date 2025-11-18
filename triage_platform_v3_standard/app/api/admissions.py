from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter()

# 🧠 simulăm o bază de date temporară (în memorie)
admissions_db = []
next_id = 1  # va fi incrementat automat


class AdmissionIn(BaseModel):
    first_name: str
    last_name: str
    triage_level: int
    triage_color: str
    reason: Optional[str] = None
    ward: Optional[str] = None
    bed: Optional[int] = None


class AdmissionOut(AdmissionIn):
    id: str
    timestamp: str


@router.post("/admissions", response_model=AdmissionOut)
def create_admission(adm: AdmissionIn):
    global next_id

    # generează un cod unic de internare
    internal_id = f"INT-{next_id:04d}"
    next_id += 1

    admission = AdmissionOut(
        id=internal_id,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **adm.dict(),
    )

    admissions_db.append(admission)
    return admission


@router.get("/admissions", response_model=List[AdmissionOut])
def list_admissions():
    """Returnează toate internările active"""
    return admissions_db
