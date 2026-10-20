
from src.agents.code_executor import validate_python_code
from src.agents.docker_sandbox import execute_python_in_sandbox


def run_with_self_debugging(code, debugger, max_attempts=3, timeout=10):
    """Execute code in Docker and request revisions after failures."""

    if not isinstance(max_attempts, int) or isinstance(max_attempts, bool) or max_attempts < 1:
        raise ValueError("max_attempts must be a positive integer.")

    if not callable(debugger):
        raise ValueError("debugger must be a callable function.")

    current_code = code
    history = []

    for attempt in range(1, max_attempts + 1):
        validation = validate_python_code(current_code)

        if not validation["valid"]:
            result = {
                "success": False,
                "stdout": "",
                "stderr": validation["error"],
                "timed_out": False,
            }
        else:
            result = execute_python_in_sandbox(
                current_code,
                timeout=timeout,
            )

        history.append({
            "attempt": attempt,
            "success": result["success"],
            "stderr": result.get("stderr", ""),
        })

        if result["success"]:
            return {
                **result,
                "attempts": attempt,
                "final_code": current_code,
                "history": history,
            }

        if attempt == max_attempts:
            break

        revised_code = debugger(
            current_code,
            result.get("stderr", ""),
        )

        if not isinstance(revised_code, str) or not revised_code.strip():
            break

        current_code = revised_code

    return {
        **result,
        "success": False,
        "attempts": len(history),
        "final_code": current_code,
        "history": history,
    }
