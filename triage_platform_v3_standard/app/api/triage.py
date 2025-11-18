from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict, Literal
from datetime import date

router = APIRouter()

# -----------------------------
# 🔹 Structuri de date
# -----------------------------
class RedFlags(BaseModel):
    active_bleeding: bool = False
    chest_pain: bool = False
    severe_dyspnea: bool = False
    anaphylaxis: bool = False
    seizure_now: bool = False
    postictal_altered: bool = False
    stroke_signs: bool = False
    pregnancy_3rd_trimester: bool = False
    major_trauma: bool = False


class TriageIn(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    cnp: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[Literal["M", "F"]] = None
    sbp: Optional[int] = None
    dbp: Optional[int] = None
    hr: Optional[int] = None
    rr: Optional[int] = None
    spo2: Optional[float] = None
    temp: Optional[float] = None
    gcs: Optional[int] = None
    pain: Optional[int] = None
    red_flags: RedFlags = RedFlags()
    resources_expected: int = 0


# -----------------------------
# 🔹 Extrage sexul și vârsta din CNP
# -----------------------------
def sex_age_from_cnp(cnp: Optional[str]) -> Dict[str, Optional[object]]:
    if not cnp or len(cnp) != 13 or not cnp.isdigit():
        return {"age": None, "sex": None}

    s = int(cnp[0])
    yy = int(cnp[1:3])
    mm = int(cnp[3:5])
    dd = int(cnp[5:7])

    # determină secolul
    if s in (1, 2):
        year = 1900 + yy
    elif s in (3, 4):
        year = 1800 + yy
    elif s in (5, 6):
        year = 2000 + yy
    else:
        year = 1900 + yy

    sex = "M" if s % 2 == 1 else "F"

    try:
        birth_date = date(year, mm, dd)
        today = date.today()
        age = today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )
    except Exception:
        age = None

    return {"age": age, "sex": sex}


# -----------------------------
# 🔹 Reguli de triaj (conform legislației)
# -----------------------------
def triage_rules(p: TriageIn):
    reasons = []
    advice = []
    p.resources_expected = p.resources_expected or 0

    # --- Pas A: ROȘU (Nivel I)
    def any_true(*vals): return any(bool(v) for v in vals)
    if (p.sbp and p.sbp < 80) or (p.spo2 and p.spo2 < 90) or (p.rr and (p.rr < 8 or p.rr > 30)) or (p.gcs and p.gcs <= 8) or \
       any_true(p.red_flags.active_bleeding, p.red_flags.severe_dyspnea, p.red_flags.anaphylaxis, p.red_flags.seizure_now, p.red_flags.major_trauma):
        reasons.append("Condiție vitală critică")
        advice = ["Anunță echipa de resuscitare", "Oxigen", "Acces venos", "Monitorizare"]
        return 1, "red", "Roșu (Nivel I - Resuscitare)", "imediat", reasons, advice

    # --- Pas B: PORTOCALIU (Nivel II)
    if (p.pain and p.pain >= 8) or (p.gcs and 9 <= p.gcs <= 12) or (p.sbp and 80 <= p.sbp < 90) or \
       (p.rr and 24 <= p.rr <= 30) or (p.spo2 and 90 <= p.spo2 <= 93) or (p.temp and p.temp >= 39.5) or p.red_flags.postictal_altered:
        reasons.append("Risc vital moderat")
        advice = ["Evaluare rapidă", "Analgezie", "Monitorizare", "Acces venos"]
        return 2, "orange", "Portocaliu (Nivel II - Critic)", "≤10 minute", reasons, advice

    # --- Pas C: Galben / Verde / Albastru
    if p.resources_expected >= 2:
        return 3, "yellow", "Galben (Nivel III - ≥2 resurse)", "≤30 minute", reasons, advice
    elif p.resources_expected == 1:
        return 4, "green", "Verde (Nivel IV - 1 resursă)", "≤60 minute", reasons, advice
    else:
        return 5, "blue", "Albastru (Nivel V - fără resurse)", "≤120 minute", reasons, advice


# -----------------------------
# 🔹 Model răspuns + Endpoint principal
# -----------------------------
class TriageOut(BaseModel):
    level: int
    color: str
    label: str
    time_target: str
    reasons: List[str]
    advice: List[str]
    normalized: Dict[str, Optional[object]]


@router.post("/triage", response_model=TriageOut)
def triage_endpoint(payload: TriageIn):
    # completează automat vârsta și sexul din CNP
    if payload.cnp and (payload.age is None or payload.sex is None):
        info = sex_age_from_cnp(payload.cnp)
        payload.age = payload.age or info.get("age")
        payload.sex = payload.sex or info.get("sex")

    level, color, label, time_target, reasons, advice = triage_rules(payload)
    norm = {"age": payload.age, "sex": payload.sex}
    return TriageOut(
        level=level, color=color, label=label, time_target=time_target,
        reasons=reasons, advice=advice, normalized=norm
    )
