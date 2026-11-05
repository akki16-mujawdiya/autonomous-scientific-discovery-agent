
from src.agents.docker_sandbox import execute_python_in_sandbox

print("ERROR TEST:")
print(execute_python_in_sandbox("raise ValueError(123)"))

print("\nTIMEOUT TEST:")
print(
    execute_python_in_sandbox(
        "import time; time.sleep(5)",
        timeout=2
    )
)
