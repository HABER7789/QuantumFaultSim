from click.testing import CliRunner
from quantumfaultsim.cli import cli


def test_sweep_integration(tmp_path):
    """
    End-to-end integration test of the sweep CLI command.
    Uses a very small parameter space (d=3, shots=500) to run quickly.
    Ensures Sinter orchestration, config, and logging all bridge correctly.
    """
    runner = CliRunner()

    # Run inside an isolated filesystem so results/ is written to tmp_path,
    # not the project root (avoids corrupting real sweep results).
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(
            cli,
            [
                "sweep",
                "--distances",
                "3,5",
                "--p-start",
                "0.01",
                "--p-end",
                "0.015",
                "--p-steps",
                "2",
                "--workers",
                "1",
                "--max-shots",
                "500",
                "--max-errors",
                "10",
            ],
        )

    assert result.exit_code == 0
    assert "Threshold sweep:" in result.output
