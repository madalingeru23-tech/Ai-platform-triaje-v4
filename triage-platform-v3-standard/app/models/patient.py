from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class PatientCreate(BaseModel):
    cnp: str = Field(..., min_length=13, max_length=13)
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None

class Patient(BaseModel):
    id: str
    cnp: str
    name: str
    birth_date: date
    age: int
    sex: str
    phone: Optional[str] = None
    address: Optional[str] = None
