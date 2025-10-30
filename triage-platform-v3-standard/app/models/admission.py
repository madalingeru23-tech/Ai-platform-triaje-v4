from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Literal

class Intervention(BaseModel):
    timestamp: datetime
    author: str
    description: str

class AdmissionCreate(BaseModel):
    patient_id: str
    reason: str
    ward: Optional[str] = None
    type: Literal["provizorie", "de zi", "continua"] = "continua"
    author: str = "admin"

class Admission(BaseModel):
    id: str
    patient_id: str
    reason: str
    ward: Optional[str] = None
    type: str
    created_at: datetime
    status: Literal["active", "discharged"]
    interventions: List[Intervention] = []
