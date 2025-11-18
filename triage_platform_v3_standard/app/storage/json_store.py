import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path("data/db.json")

def _empty_db():
    return {"patients": {}, "admissions": {}, "last_ids": {"patients": 0, "admissions": 0}}

def load_db():
    if not DB_PATH.exists():
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        db = _empty_db()
        save_db(db)
        return db
    with DB_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db: dict):
    with DB_PATH.open("w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2, default=_json_default)

def _json_default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)

def get_next_id(db: dict, key: str) -> str:
    db["last_ids"][key] += 1
    return str(db["last_ids"][key])
