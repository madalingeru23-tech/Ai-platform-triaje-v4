import json
import os
from typing import Optional, Dict, Any, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "doctors.json")

def _load_all() -> List[Dict[str, Any]]:
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_by_id(doc_id: int) -> Optional[Dict[str, Any]]:
    for d in _load_all():
        if d.get("id") == doc_id:
            return d
    return None

def find_by_pin_hash(pin_hash: str) -> Optional[Dict[str, Any]]:
    for d in _load_all():
        if d.get("pin_hash") == pin_hash:
            return d
    return None
