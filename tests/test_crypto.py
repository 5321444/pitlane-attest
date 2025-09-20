from pitlane_attest.crypto import ensure_keys, sign_attestation, verify_attestation
from pitlane_attest.models import Attestation, TelemetryRef


def test_sign_verify_roundtrip():
    keys = ensure_keys()
    att = Attestation(
        schema="pitlane.attestation/0.1",
        action_id="test-1",
        agent_id="agent-x",
        policy_id="policy-1",
        env="sim",
        risk="low",
        timestamp=1234567890,
        telemetry=TelemetryRef(kind="json", path="demo.json", sha256="00" * 32),
    )
    att = sign_attestation(att, keys["ed25519_secret_hex"])
    assert verify_attestation(att) is True
