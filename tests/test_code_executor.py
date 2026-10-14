
from src.agents.code_executor import validate_python_code


def test_valid_python_code():
    code = "x = 10\nprint(x)"

    result = validate_python_code(code)

    assert result["valid"] is True
    assert result["error"] is None


def test_invalid_python_code():
    code = "if True print('Hello')"

    result = validate_python_code(code)

    assert result["valid"] is False
    assert result["error"] is not None


def test_empty_python_code():
    result = validate_python_code("")

    assert result["valid"] is True
    assert result["error"] is None
