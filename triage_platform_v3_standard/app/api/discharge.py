from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
import json

router = APIRouter()

# 📂 unde salvăm "experiența" AI-ului
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LEARN_FILE = os.path.join(DATA_DIR, "discharge_learning.json")


class DischargeSuggestIn(BaseModel):
    triage_level: int
    reason: Optional[str] = None


class DischargeSuggestion(BaseModel):
    diagnosis: str
    evolution: str
    recommendations: str


class DischargeConfirmIn(BaseModel):
    triage_level: int
    reason: Optional[str] = None
    diagnosis_final: str
    evolution_final: str
    recommendations_final: str


def _load_learning() -> List[dict]:
    if not os.path.exists(LEARN_FILE):
        return []
    try:
        with open(LEARN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # dacă s-a corupt fișierul, nu omorâm serverul
        return []


def _append_learning(entry: dict) -> None:
    data = _load_learning()
    data.append(entry)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(LEARN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _default_templates(level: int, reason: Optional[str]) -> DischargeSuggestion:
    motiv = reason or "afecțiune acută, evaluată în regim de ambulator"
    if level == 1:
        diag = f"Stare critică evaluată în UPU pentru {motiv}."
        evo = "Pacient evaluat în urgență majoră. Stabilizare inițială efectuată, este necesară supraveghere de specialitate și eventual internare."
        rec = "Continuă prezentarea de urgență la cel mai apropiat spital și respectarea indicațiilor medicului curant."
    elif level == 2:
        diag = f"Episod acut cu potențial de agravare, cu adresare în UPU pentru {motiv}."
        evo = "Simptomatologia s-a ameliorat parțial după tratamentul instituit în serviciul de urgență."
        rec = "Se recomandă monitorizarea atentă a simptomelor și prezentare la medicul specialist sau UPU dacă apar agravări."
    elif level == 3:
        diag = f"{motiv.capitalize()} cu risc moderat, adecvat tratamentului în ambulator."
        evo = "Evoluție favorabilă pe durata observației, fără criterii actuale de internare."
        rec = "Tratament simptomatic conform recomandărilor, control la medicul de familie / medicul specialist și reevaluare dacă simptomele persistă sau se agravează."
    elif level == 4:
        diag = f"{motiv.capitalize()} cu severitate ușoară, stabilă clinic."
        evo = "Stare generală bună, parametri vitali în limite acceptabile, fără modificări acute majore."
        rec = "Continuarea tratamentului la domiciliu, stil de viață adecvat și control periodic la medicul de familie."
    else:  # 5 sau orice altceva
        diag = f"Consult de rutină / simptome minore: {motiv}."
        evo = "Nu se evidențiază modificări acute semnificative la examenul obiectiv și investigațiile disponibile."
        rec = "Recomandări de stil de viață, eventual tratament simptomatic la nevoie și prezentare la medicul de familie pentru urmărire."

    return DischargeSuggestion(
        diagnosis=diag,
        evolution=evo,
        recommendations=rec,
    )


@router.post("/discharge/suggest", response_model=DischargeSuggestion)
def suggest_discharge(payload: DischargeSuggestIn):
    """
    1) încearcă să găsească cazuri similare în istoricul salvat
    2) dacă nu găsește, folosește șabloanele implicite pe nivel de triaj
    """
    if payload.triage_level < 1 or payload.triage_level > 5:
        raise HTTPException(status_code=400, detail="Nivel de triaj invalid (1–5).")

    learned = _load_learning()
    reason_lower = (payload.reason or "").lower().strip()

    for row in reversed(learned):
        if row.get("triage_level") != payload.triage_level:
            continue

        # dacă motivul e asemănător, preferăm acest caz
        prev_reason = (row.get("reason") or "").lower().strip()
        if reason_lower and prev_reason and (
            reason_lower in prev_reason or prev_reason in reason_lower
        ):
            return DischargeSuggestion(
                diagnosis=row.get("diagnosis_final", ""),
                evolution=row.get("evolution_final", ""),
                recommendations=row.get("recommendations_final", ""),
            )

    # nu avem nimic potrivit în "memorie" -> șablon implicit
    return _default_templates(payload.triage_level, payload.reason)


@router.post("/discharge/confirm")
def confirm_discharge(payload: DischargeConfirmIn):
    """
    Salvează varianta FINALĂ (confirmată / modificată de medic)
    ca să poată fi propusă la cazuri similare în viitor.
    """
    entry = payload.model_dump()
    _append_learning(entry)
    return {"ok": True}
