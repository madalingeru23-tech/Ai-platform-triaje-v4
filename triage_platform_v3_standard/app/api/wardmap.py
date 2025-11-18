from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

# 🔹 Router clar înregistrat cu tag vizibil în Swagger
router = APIRouter(prefix="/wardmap", tags=["Wardmap"])

# 🧠 model pentru cererea primită
class WardSuggestionIn(BaseModel):
    triage_level: int
    triage_color: str
    reason: Optional[str] = None

# 🔹 răspunsul trimis către frontend
class WardSuggestionOut(BaseModel):
    suggested_ward: str
    confidence: float
    comment: str

@router.post("/suggest", response_model=WardSuggestionOut)
def suggest_ward(data: WardSuggestionIn):
    """
    Returnează o sugestie AI imaginară pentru secția de internare.
    Într-o versiune viitoare, logica va fi bazată pe modele AI reale.
    """
    color = data.triage_color.lower()
    level = data.triage_level

    # logica simplificată de exemplu:
    if color in ["red", "roșu"] or level == 1:
        ward = "Terapie Intensivă"
        confidence = 0.98
    elif color in ["orange", "portocaliu"] or level == 2:
        ward = "Cardiologie / UPU Critici"
        confidence = 0.91
    elif color in ["yellow", "galben"] or level == 3:
        ward = "Secția Medicină Internă"
        confidence = 0.87
    elif color in ["green", "verde"] or level == 4:
        ward = "Ambulatoriu"
        confidence = 0.80
    else:
        ward = "Observație / Externare"
        confidence = 0.75

    comment = f"Pacientul de nivel {level} ({color.upper()}) este potrivit pentru {ward.lower()}."
    return WardSuggestionOut(suggested_ward=ward, confidence=confidence, comment=comment)
