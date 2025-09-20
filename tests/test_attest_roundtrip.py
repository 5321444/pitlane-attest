from typer.testing import CliRunner

from pitlane_attest.cli import app
from pitlane_attest.crypto import ensure_keys


def test_cli_attest(tmp_path):
    ensure_keys()
    telemetry = tmp_path / "t.json"
    telemetry.write_text('{"hello":"world"}', encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "attest",
            "--action-id",
            "demo",
            "--agent-id",
            "bot-1",
            "--policy-id",
            "base-1",
            "--env",
            "sim",
            "--risk",
            "low",
            "--telemetry",
            str(telemetry),
            "--notes",
            "test",
        ],
    )
    assert result.exit_code == 0
