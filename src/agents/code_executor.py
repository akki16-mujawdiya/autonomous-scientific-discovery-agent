
import ast


def validate_python_code(code):
    """
    Check whether Python code has valid syntax.
    Does not execute the code.
    """
    try:
        ast.parse(code)
    except SyntaxError as error:
        return {
            "valid": False,
            "error": str(error),
        }

    return {
        "valid": True,
        "error": None,
    }
