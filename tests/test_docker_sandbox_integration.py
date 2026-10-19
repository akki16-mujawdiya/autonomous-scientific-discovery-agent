
import shutil
import subprocess

import pytest

from src.agents.docker_sandbox import execute_python_in_sandbox


def docker_is_available():
    if shutil.which("docker") is None:
        return False

    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


pytestmark = pytest.mark.skipif(
    not docker_is_available(),
    reason="Docker CLI or Docker daemon is unavailable",
)


def test_real_container_executes_python():
    result = execute_python_in_sandbox("print(1 + 1)")

    assert result["success"] is True
    assert result["stdout"].strip() == "2"
    assert result["returncode"] == 0


def test_real_container_reports_python_error():
    result = execute_python_in_sandbox("raise ValueError(123)")

    assert result["success"] is False
    assert "ValueError: 123" in result["stderr"]
    assert result["returncode"] != 0


def test_real_container_enforces_timeout():
    result = execute_python_in_sandbox(
        "import time; time.sleep(5)",
        timeout=2,
    )

    assert result["success"] is False
    assert result["timed_out"] is True
