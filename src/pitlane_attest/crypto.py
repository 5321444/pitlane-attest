import hashlib
import json
from pathlib import Path

from nacl import signing

from .models import Attestation, canonical_json

KEY_PATH = Path.home() / ".pitlane" / "keys.json"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def ensure_keys() -> dict[str, str]:
    if KEY_PATH.exists():
        return json.loads(KEY_PATH.read_text(encoding="utf-8"))
    KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    sk = signing.SigningKey.generate()
    vk = sk.verify_key
    data = {"ed25519_secret_hex": sk.encode().hex(), "ed25519_public_hex": vk.encode().hex()}
    KEY_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def load_keys() -> dict[str, str]:
    if not KEY_PATH.exists():
        raise FileNotFoundError("No keys; run `pitlane-attest init-key` first.")
    return json.loads(KEY_PATH.read_text(encoding="utf-8"))


def sign_attestation(att: Attestation, secret_hex: str) -> Attestation:
    sk = signing.SigningKey(bytes.fromhex(secret_hex))
    payload = canonical_json(att.to_signable())
    sig = sk.sign(payload.encode("utf-8")).signature.hex()
    att.signature = sig
    att.signer_pub = sk.verify_key.encode().hex()
    return att


def verify_attestation(att: Attestation) -> bool:
    if not att.signature or not att.signer_pub:
        return False
    vk = signing.VerifyKey(bytes.fromhex(att.signer_pub))
    payload = canonical_json(att.to_signable()).encode("utf-8")
    try:
        vk.verify(payload, bytes.fromhex(att.signature))
        return True
    except Exception:
        return False
