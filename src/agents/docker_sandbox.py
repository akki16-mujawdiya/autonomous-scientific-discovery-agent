
import subprocess
import tempfile
from pathlib import Path


DEFAULT_TIMEOUT = 10


def execute_python_in_sandbox(code, timeout=DEFAULT_TIMEOUT):
    """
    Execute Python code inside a restricted Docker container.
    The submitted code is never executed directly on the host.
    """
    if not isinstance(code, str) or not code.strip():
        return {
            "success": False,
            "stdout": "",
            "stderr": "Python code cannot be empty.",
            "timed_out": False,
        }

    if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or timeout <= 0:
        raise ValueError("Timeout must be a positive number.")

    with tempfile.TemporaryDirectory(prefix="scientific_sandbox_") as temp_dir:
        work_dir = Path(temp_dir)
        script_path = work_dir / "main.py"
        script_path.write_text(code, encoding="utf-8")

        mount_source = work_dir.as_posix()

        command = [
            "docker", "run", "--rm",
            "--network", "none",
            "--read-only",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            "--memory", "256m",
            "--cpus", "1",
            "--pids-limit", "64",
            "--user", "65534:65534",
            "--mount",
            f"type=bind,source={mount_source},target=/workspace,readonly",
            "--workdir", "/workspace",
            "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m",
            "--env", "PYTHONDONTWRITEBYTECODE=1",
            "python:3.12-slim",
            "python", "-I", "/workspace/main.py",
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "timed_out": False,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution exceeded {timeout} seconds.",
                "timed_out": True,
            }

        except OSError as error:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Could not start Docker: {error}",
                "timed_out": False,
            }
