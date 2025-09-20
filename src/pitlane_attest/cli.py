import json
import os
import time
from typing import Optional

import typer
from rich import print as rprint

from .crypto import ensure_keys, load_keys, sign_attestation, verify_attestation
from .io import detect_telemetry, make_bundle, write_attestation
from .models import Attestation, TelemetryRef

app = typer.Typer(add_completion=False, help="Pitlane attestation toolkit")


@app.command()
def init_key():
    """Generate or show local Ed25519 keypair (~/.pitlane/keys.json)."""
    keys = ensure_keys()
    rprint({"public_key": keys["ed25519_public_hex"], "key_path": str(keys)})


@app.command()
def attest(
    action_id: str = typer.Option(..., help="Unique action id (e.g., deploy-2025-09-20a)"),
    agent_id: str = typer.Option(..., help="Robot/agent id"),
    policy_id: str = typer.Option(..., help="Policy id at decision time"),
    env: str = typer.Option("sim", help="sim|prod"),
    risk: str = typer.Option("med", help="low|med|high"),
    telemetry: str = typer.Option(..., help="Path to telemetry .json or .db3"),
    notes: Optional[str] = typer.Option(None, help="Optional freeform notes"),
    out_dir: str = typer.Option("attestations", help="Output directory for attestation JSON"),
):
    keys = load_keys()
    kind, sha = detect_telemetry(telemetry)
    tref = TelemetryRef(kind=kind, path=os.path.basename(telemetry), sha256=sha)
    att = Attestation(
        schema="pitlane.attestation/0.1",
        action_id=action_id,
        agent_id=agent_id,
        policy_id=policy_id,
        env=env,
        risk=risk,
        timestamp=int(time.time()),
        telemetry=tref,
        notes=notes,
    )
    att = sign_attestation(att, keys["ed25519_secret_hex"])
    out = write_attestation(att, out_dir)
    rprint({"attestation": out, "signature_valid": verify_attestation(att)})


@app.command()
def verify(attestation_path: str = typer.Argument(...), telemetry_path: str = typer.Argument(...)):
    """Verify signature and telemetry hash match."""
    data = json.loads(open(attestation_path, encoding="utf-8").read())
    from .models import Attestation, TelemetryRef

    att = Attestation(
        **{
            **{k: v for k, v in data.items() if k not in ("telemetry",)},
            "telemetry": TelemetryRef(**data["telemetry"]),
        }
    )
    ok_sig = verify_attestation(att)
    from .crypto import sha256_file

    ok_hash = att.telemetry.sha256 == sha256_file(telemetry_path)
    rprint({"signature_ok": ok_sig, "telemetry_hash_ok": ok_hash})


@app.command()
def bundle(attestation_path: str, telemetry_path: str, out_dir: str = "bundles"):
    """Create a portable .tar.gz with attestation, telemetry, and a replay manifest."""
    bundle_path = make_bundle(attestation_path, telemetry_path, out_dir)
    rprint({"bundle": bundle_path})


if __name__ == "__main__":
    app()
