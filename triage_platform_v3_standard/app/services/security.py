import hashlib

_SALT = "triage_local_salt_v1"

def hash_pin(pin: str) -> str:
    s = f"{_SALT}:{pin}".encode("utf-8")
    return hashlib.sha256(s).hexdigest()

def verify_pin(pin: str, pin_hash: str) -> bool:
    return hash_pin(pin) == pin_hash
