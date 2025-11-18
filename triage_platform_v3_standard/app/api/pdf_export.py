from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
from io import BytesIO
import unicodedata

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

from PyPDF2 import PdfMerger
from PyPDF2.errors import PdfReadError

from .auth import get_current_doctor, DoctorPublic

router = APIRouter()

# -------------------------------------------------------------------------
# CONFIG SPITAL + PATH-URI
# -------------------------------------------------------------------------
HOSPITAL_NAME = "ArmoniaLife Hospital"
HOSPITAL_ADDRESS = "Str. Bld Serantei, 110, Iasi, Iasi"

BASE_DIR = Path(__file__).resolve().parents[2]
STATIC_DIR = BASE_DIR / "static"
IMG_DIR = STATIC_DIR / "img"
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

LOGO_PATH = IMG_DIR / "logo.png"


# -------------------------------------------------------------------------
# UTILS
# -------------------------------------------------------------------------
def strip_accents(text: str) -> str:
    """Elimina diacriticele pentru a evita probleme cu fonturile din PDF."""
    if not text:
        return ""
    text = unicodedata.normalize("NFD", text)
    return "".join(c for c in text if not unicodedata.combining(c))


def split_text(text: str, max_len: int = 100):
    """Împarte un text lung în linii scurte pentru PDF."""
    text = text or ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    parts = []
    for paragraph in text.split("\n"):
        p = paragraph.strip()
        if not p:
            parts.append("")   # linie goală
            continue
        while len(p) > max_len:
            cut = p.rfind(" ", 0, max_len)
            if cut == -1:
                cut = max_len
            parts.append(p[:cut])
            p = p[cut:].lstrip()
        if p:
            parts.append(p)
    return parts


def url_to_fs_path(url: str) -> Optional[Path]:
    """Transformă ceva de genul '/static/img/parafa.png' în cale pe disc."""
    if not url:
        return None
    if not url.startswith("/static/"):
        return None
    rel = url.replace("/static/", "")
    return STATIC_DIR / rel


# -------------------------------------------------------------------------
# MODEL DE INPUT
# -------------------------------------------------------------------------
class ExternareIn(BaseModel):
    # date pacient
    patient_name: str
    cnp: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None

    # conținut medical
    diagnosis: str
    evolution: str
    recommendations: str

    # info triage
    triage_level: Optional[int] = None
    triage_color: Optional[str] = None
    reason: Optional[str] = None

    # lista de fișiere PDF salvate la upload
    investigations: List[str] = []          # numele din frontend
    attached_pdfs: List[str] = []          # fallback dacă mai folosești numele vechi

    class Config:
        orm_mode = True


# -------------------------------------------------------------------------
# HEADER (logo + nume spital + titlu)
# -------------------------------------------------------------------------
def draw_header(c: canvas.Canvas):
    width, height = A4
    y = height - 40

    # logo
    if LOGO_PATH.exists():
        try:
            c.drawImage(
                str(LOGO_PATH),
                40, y - 55,
                width=70, height=70,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception:
            pass

    # nume spital
    c.setFont("Helvetica-Bold", 16)
    c.drawString(130, y, strip_accents(HOSPITAL_NAME))

    c.setFont("Helvetica", 10)
    c.drawString(130, y - 20, strip_accents(HOSPITAL_ADDRESS))

    # titlu
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(
        width / 2,
        y - 70,
        strip_accents("FOAIE DE EXTERNARE – AMBULATORIU"),
    )

    # linie sub titlu
    c.setLineWidth(1.2)
    c.line(40, y - 85, width - 40, y - 85)


# -------------------------------------------------------------------------
# SEMNĂTURĂ + PARAFA
# -------------------------------------------------------------------------
def draw_signature(c: canvas.Canvas, doctor: DoctorPublic):
    width, height = A4

    base_x = 70
    base_y = 150

    # text "medic curant"
    c.setFont("Helvetica", 10)
    c.drawString(base_x, base_y + 50, "Medic curant:")
    c.setFont("Helvetica-Bold", 11)
    c.drawString(base_x, base_y + 35, strip_accents(doctor.full_name))
    c.setFont("Helvetica", 9)
    c.drawString(base_x, base_y + 22, strip_accents(doctor.specialty or ""))

    # parafa la ~2px de text
    stamp_path = url_to_fs_path(getattr(doctor, "stamp_url", None))
    stamp_x = base_x + 90   # puțin în dreapta de text
    stamp_y = base_y + 18

    if stamp_path and stamp_path.exists():
        try:
            img_stamp = ImageReader(str(stamp_path))
            c.drawImage(
                img_stamp,
                stamp_x,
                stamp_y,
                width=90,
                height=55,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception:
            pass

    # semnatura sub parafă
    sign_path = url_to_fs_path(getattr(doctor, "signature_url", None))
    sign_x = stamp_x + 10
    sign_y = stamp_y - 55

    if sign_path and sign_path.exists():
        try:
            img_sign = ImageReader(str(sign_path))
            c.drawImage(
                img_sign,
                sign_x,
                sign_y,
                width=120,
                height=60,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception:
            pass


# -------------------------------------------------------------------------
# BODY (conținut foaie externare)
# -------------------------------------------------------------------------
def draw_body(c: canvas.Canvas, data: ExternareIn, doctor: DoctorPublic):
    width, height = A4
    y = height - 150

    c.setFont("Helvetica", 11)

    # pacient
    c.drawString(40, y, strip_accents(f"Pacient: {data.patient_name or '-'}"))
    y -= 15

    if data.cnp:
        c.drawString(40, y, strip_accents(f"CNP: {data.cnp}"))
        y -= 15

    if data.age is not None or data.sex:
        c.drawString(
            40,
            y,
            strip_accents(
                f"Varsta/Sex: {data.age if data.age is not None else '-'} / "
                f"{data.sex or '-'}"
            ),
        )
        y -= 15

    if data.triage_level:
        c.drawString(
            40,
            y,
            strip_accents(f"Nivel triaj: {data.triage_level}"),
        )
        y -= 25

    # Diagnostic
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y, "Diagnostic:")
    y -= 15
    c.setFont("Helvetica", 10)
    for line in split_text(strip_accents(data.diagnosis)):
        c.drawString(55, y, line)
        y -= 14

    y -= 10

    # Evoluție
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y, "Evolutie:")
    y -= 15
    c.setFont("Helvetica", 10)
    for line in split_text(strip_accents(data.evolution)):
        c.drawString(55, y, line)
        y -= 14

    y -= 10

    # Recomandări
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y, "Recomandari:")
    y -= 15
    c.setFont("Helvetica", 10)
    for line in split_text(strip_accents(data.recommendations)):
        c.drawString(55, y, line)
        y -= 14

    # semnătura + parafa
    draw_signature(c, doctor)


# -------------------------------------------------------------------------
# UPLOAD PDF INVESTIGAȚII
# -------------------------------------------------------------------------
@router.post("/uploads/investigatie")
async def upload_investigatie(file: UploadFile = File(...)):
    """
    Upload pentru un singur PDF de investigații.
    Returnează numele sub care a fost salvat pe server.
    """
    filename = file.filename or "investigatie.pdf"

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Se accepta doar fisiere PDF.")

    safe_name = filename.replace("/", "_").replace("\\", "_")
    dest = UPLOAD_DIR / safe_name

    content = await file.read()
    if not content.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="Fisier PDF invalid.")

    dest.write_bytes(content)

    return {"stored_name": safe_name}
    # frontend-ul va folosi stored_name în lista de investigations


# -------------------------------------------------------------------------
# GENERARE PDF FINAL (foaie + investigatii atasate)
# -------------------------------------------------------------------------
@router.post("/pdf/externare")
def generate_pdf(
    data: ExternareIn,
    doctor: DoctorPublic = Depends(get_current_doctor),
):
    """
    Genereaza foaia de externare si, daca exista,
    ataseaza PDF-urile de investigatii ca pagini suplimentare.
    """

    if not doctor:
        raise HTTPException(status_code=401, detail="Neautentificat")

    # ----------------- 1. Pagina principală -----------------
    base_buffer = BytesIO()
    c = canvas.Canvas(base_buffer, pagesize=A4)

    draw_header(c)
    draw_body(c, data, doctor)

    c.showPage()
    c.save()
    base_buffer.seek(0)

    # Colectăm lista de PDF-uri atașate (acceptăm și field-ul vechi)
    pdf_list = data.investigations or data.attached_pdfs or []

    # Dacă nu avem nimic de atașat → doar foaia de externare
    if not pdf_list:
        return StreamingResponse(
            base_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=externare.pdf"},
        )

    # ----------------- 2. Facem merge cu investigațiile -----------------
    merger = PdfMerger()
    merger.append(base_buffer)

    for name in pdf_list:
        path = UPLOAD_DIR / name
        if not path.exists():
            continue
        try:
            merger.append(str(path))
        except PdfReadError:
            # dacă fișierul e corupt, îl sărim
            continue
        except Exception:
            continue

    final_buffer = BytesIO()
    merger.write(final_buffer)
    merger.close()
    final_buffer.seek(0)

    return StreamingResponse(
        final_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=externare.pdf"},
    )