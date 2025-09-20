# Pitlane Attest

Cryptographic attestation toolkit for robotics safety and compliance. Generate verifiable proof of robot actions with policy context, telemetry integrity, and audit trails. Designed for production robotics teams requiring demonstrable safety compliance.

## Overview

Robots perform safety-critical actions that require verifiable proof of execution context. This toolkit provides:

- **Cryptographic attestations** for robot actions with policy binding
- **Telemetry integrity verification** via SHA-256 hashing
- **Sim-to-production traceability** with environment tagging
- **Audit trail generation** for compliance and debugging
- **Portable replay bundles** for incident investigation

## Installation

```bash
python -m pip install --upgrade pip
pip install -e .
```

## Quick Start

```bash
# Initialize cryptographic keys
pitlane-attest init-key

# Create attestation for robot action
pitlane-attest attest \
  --action-id pick-object-001 \
  --agent-id arm-robot-05 \
  --policy-id safety-v2.1 \
  --env sim \
  --risk med \
  --telemetry robot_telemetry.json \
  --notes "Simulation rehearsal before production"

# Verify attestation integrity
pitlane-attest verify \
  attestations/pick-object-001-<timestamp>.attestation.json \
  robot_telemetry.json

# Create portable investigation bundle
pitlane-attest bundle \
  attestations/pick-object-001-<timestamp>.attestation.json \
  robot_telemetry.json
```

## Use Cases

- **Safety compliance**: Prove robot actions followed approved policies
- **Incident investigation**: Replay exact robot state and decision context
- **Sim-to-real validation**: Verify simulation actions before production deployment
- **Audit trails**: Generate tamper-proof logs for regulatory compliance
- **Debugging**: Cryptographically verify telemetry data integrity

## Data Model

**Attestation Schema** (`pitlane.attestation/0.1`):
- `action_id`: Unique identifier for the robot action
- `agent_id`: Robot/agent identifier
- `policy_id`: Safety policy version at decision time
- `env`: Environment context (`sim` or `prod`)
- `risk`: Risk level assessment (`low`, `med`, `high`)
- `timestamp`: Unix epoch timestamp
- `telemetry`: Reference to telemetry data with SHA-256 hash
- `signature`: Ed25519 cryptographic signature
- `signer_pub`: Public key for signature verification

**Telemetry Support**:
- JSON files (universal compatibility)
- ROS2 rosbag2 `.db3` files (optional, graceful fallback)
- Deterministic canonicalization for consistent hashing

## Integration

The toolkit integrates with existing robotics workflows:

```python
# In your robot control loop
import json
import subprocess

# Log telemetry
telemetry = {
    "agent": "robot-01",
    "pose": {"x": 1.2, "y": 3.4, "z": 0.5},
    "action": "pick_object",
    "sensors": {"camera": "ok", "force": 18.2}
}

with open("telemetry.json", "w") as f:
    json.dump(telemetry, f)

# Create attestation
subprocess.run([
    "pitlane-attest", "attest",
    "--action-id", "pick-001",
    "--agent-id", "robot-01", 
    "--policy-id", "safety-v1.2",
    "--env", "prod",
    "--risk", "med",
    "--telemetry", "telemetry.json"
])
```

## Security

- **Ed25519 signatures** via PyNaCl for cryptographic verification
- **SHA-256 hashing** for telemetry integrity
- **Deterministic JSON serialization** for consistent signing
- **Key management** via `~/.pitlane/keys.json`

## License

Apache-2.0
