from fastapi import APIRouter, Response, Depends, HTTPException, Cookie
from pydantic import BaseModel
from typing import Optional, Dict
import uuid

from ..services.security import verify_pin, hash_pin
from ..storage.doctor_store import find_by_pin_hash, get_by_id

router = APIRouter()

# Sesiuni simple in-memorie (dev). Cheia = session_id, valoarea = doctor_id
_SESSIONS: Dict[str, int] = {}

class LoginIn(BaseModel):
    pin: str

class DoctorPublic(BaseModel):
    id: int
    full_name: str
    specialty: str
    stamp_url: str
    signature_url: str

def _to_public(d) -> DoctorPublic:
    return DoctorPublic(
        id=d["id"],
        full_name=f'{d.get("last_name","")} {d.get("first_name","")}'.strip(),
        specialty=d.get("specialty",""),
        stamp_url=d.get("stamp_url",""),
        signature_url=d.get("signature_url",""),
    )

def get_current_doctor(session_id: Optional[str] = Cookie(default=None)) -> Optional[DoctorPublic]:
    if not session_id:
        return None
    doc_id = _SESSIONS.get(session_id)
    if not doc_id:
        return None
    d = get_by_id(doc_id)
    return _to_public(d) if d else None

@router.post("/auth/login", response_model=DoctorPublic)
def login(payload: LoginIn, response: Response):
    if not payload.pin or len(payload.pin) != 4 or not payload.pin.isdigit():
        raise HTTPException(status_code=400, detail="PIN invalid (4 cifre).")
    ph = hash_pin(payload.pin)
    d = find_by_pin_hash(ph)
    if not d:
        raise HTTPException(status_code=401, detail="PIN greșit.")
    # creăm sesiune și setăm cookie httpOnly
    sid = uuid.uuid4().hex
    _SESSIONS[sid] = d["id"]
    response.set_cookie(
        key="session_id",
        value=sid,
        httponly=True,
        samesite="lax",
        max_age=60*60*12  # 12h
    )
    return _to_public(d)

@router.post("/auth/logout")
def logout(response: Response, session_id: Optional[str] = Cookie(default=None)):
    if session_id and session_id in _SESSIONS:
        _SESSIONS.pop(session_id, None)
    response.delete_cookie("session_id")
    return {"ok": True}

@router.get("/auth/me", response_model=DoctorPublic)
def me(current: Optional[DoctorPublic] = Depends(get_current_doctor)):
    if not current:
        raise HTTPException(status_code=401, detail="Neautentificat.")
    return current
