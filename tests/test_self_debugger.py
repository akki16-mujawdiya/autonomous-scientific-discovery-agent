
from unittest.mock import patch

import pytest

from src.agents.self_debugger import run_with_self_debugging


def test_successful_execution():
    with patch(
        "src.agents.self_debugger.execute_python_in_sandbox",
        return_value={
            "success": True,
            "stdout": "2\n",
            "stderr": "",
            "returncode": 0,
            "timed_out": False,
        },
    ):
        result = run_with_self_debugging(
            "print(1 + 1)",
            debugger=lambda code, error: code,
        )

    assert result["success"] is True
    assert result["attempts"] == 1


def test_retries_with_revised_code():
    responses = [
        {
            "success": False,
            "stdout": "",
            "stderr": "NameError",
            "returncode": 1,
            "timed_out": False,
        },
        {
            "success": True,
            "stdout": "2\n",
            "stderr": "",
            "returncode": 0,
            "timed_out": False,
        },
    ]

    with patch(
        "src.agents.self_debugger.execute_python_in_sandbox",
        side_effect=responses,
    ) as execute:
        result = run_with_self_debugging(
            "print(x)",
            debugger=lambda code, error: "print(1 + 1)",
        )

    assert result["success"] is True
    assert result["attempts"] == 2
    assert execute.call_count == 2


def test_stops_after_max_attempts():
    with patch(
        "src.agents.self_debugger.execute_python_in_sandbox",
        return_value={
            "success": False,
            "stdout": "",
            "stderr": "RuntimeError",
            "returncode": 1,
            "timed_out": False,
        },
    ) as execute:
        result = run_with_self_debugging(
            "raise RuntimeError()",
            debugger=lambda code, error: code,
            max_attempts=3,
        )

    assert result["success"] is False
    assert result["attempts"] == 3
    assert execute.call_count == 3


def test_rejects_invalid_max_attempts():
    with pytest.raises(ValueError):
        run_with_self_debugging(
            "print(1)",
            debugger=lambda code, error: code,
            max_attempts=0,
        )


def test_rejects_missing_debugger():
    with pytest.raises(ValueError):
        run_with_self_debugging("print(1)", debugger=None)
