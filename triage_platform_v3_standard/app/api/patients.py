from fastapi import APIRouter

router = APIRouter()

@router.get("/patients")
def list_patients():
    return []
