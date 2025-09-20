import json
import os

from .crypto import sha256_file
from .models import Attestation


def detect_telemetry(path: str) -> tuple[str, str]:
    lower = path.lower()
    if lower.endswith(".json"):
        kind = "json"
    elif lower.endswith(".db3") or lower.endswith(".bag"):
        kind = "rosbag2"
    else:
        kind = "unknown"
    return kind, sha256_file(path)


def write_attestation(att: Attestation, out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    fname = f"{att.action_id}-{att.timestamp}.attestation.json"
    out_path = os.path.join(out_dir, fname)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(att.to_json())
    return out_path


def make_bundle(att_path: str, telemetry_path: str, out_dir: str) -> str:
    import os
    import tarfile
    import time

    os.makedirs(out_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(att_path))[0]
    bundle_path = os.path.join(out_dir, f"{base}.tar.gz")
    manifest = {
        "schema": "pitlane.bundle/0.1",
        "created": int(time.time()),
        "attestation": os.path.basename(att_path),
        "telemetry": os.path.basename(telemetry_path),
        "replay": {
            "kind": "hint",
            "cmd_examples": [
                "ros2 bag play <telemetry.db3>  # if available",
                "python -m json.tool <telemetry.json>",
            ],
        },
    }
    manifest_path = os.path.join(os.path.dirname(att_path), f"{base}.replay.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(manifest, indent=2))
    with tarfile.open(bundle_path, "w:gz") as tar:
        tar.add(att_path, arcname=os.path.basename(att_path))
        tar.add(telemetry_path, arcname=os.path.basename(telemetry_path))
        tar.add(manifest_path, arcname=os.path.basename(manifest_path))
    return bundle_path
