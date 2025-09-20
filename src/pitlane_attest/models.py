import json
import time
from dataclasses import asdict, dataclass
from typing import Any, Optional


def canonical_json(obj: dict[str, Any]) -> str:
    # Simple canonicalization: sorted keys, compact separators
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass
class TelemetryRef:
    kind: str  # "json" | "rosbag2"
    path: str
    sha256: str


@dataclass
class Attestation:
    schema: str
    action_id: str
    agent_id: str
    policy_id: str
    env: str  # "sim" | "prod"
    risk: str  # "low" | "med" | "high"
    timestamp: int  # epoch seconds
    telemetry: TelemetryRef
    notes: Optional[str] = None
    signature: Optional[str] = None  # hex
    signer_pub: Optional[str] = None  # hex

    def to_signable(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("signature", None)
        d.pop("signer_pub", None)
        return d

    def to_json(self) -> str:
        return canonical_json(asdict(self))

    @staticmethod
    def now_epoch() -> int:
        return int(time.time())
