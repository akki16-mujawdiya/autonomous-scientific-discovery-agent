
from unittest.mock import Mock, patch

from src.agents.docker_sandbox import execute_python_in_sandbox


@patch("src.agents.docker_sandbox.subprocess.run")
def test_successful_execution(mock_run):
    mock_run.return_value = Mock(
        returncode=0,
        stdout="2\n",
        stderr="",
    )

    result = execute_python_in_sandbox("print(1 + 1)")

    assert result["success"] is True
    assert result["stdout"] == "2\n"
    assert result["timed_out"] is False

    command = mock_run.call_args.args[0]
    assert "--network" in command
    assert "none" in command
    assert "--read-only" in command
    assert "--cap-drop" in command
    assert "ALL" in command


@patch("src.agents.docker_sandbox.subprocess.run")
def test_execution_error(mock_run):
    mock_run.return_value = Mock(
        returncode=1,
        stdout="",
        stderr="NameError",
    )

    result = execute_python_in_sandbox("print(unknown_variable)")

    assert result["success"] is False
    assert "NameError" in result["stderr"]


@patch("src.agents.docker_sandbox.subprocess.run")
def test_execution_timeout(mock_run):
    from subprocess import TimeoutExpired

    mock_run.side_effect = TimeoutExpired(
        cmd="docker",
        timeout=1,
    )

    result = execute_python_in_sandbox(
        "while True: pass",
        timeout=1,
    )

    assert result["success"] is False
    assert result["timed_out"] is True


def test_empty_code_is_rejected():
    result = execute_python_in_sandbox("")

    assert result["success"] is False
    assert "empty" in result["stderr"].lower()


def test_invalid_timeout_is_rejected():
    import pytest

    with pytest.raises(ValueError):
        execute_python_in_sandbox("print('hello')", timeout=0)
