import os
import os.path
import subprocess
import sys
from typing import List, Optional
from google.genai import types

def run_python_file(working_directory: str, file_path: str, args: Optional[List[str]] = None) -> str:
    """
    Executes a Python file within a restricted working directory using subprocess.run.

    Args:
        working_directory: The root directory the LLM is allowed to access.
        file_path: The relative path to the Python file to execute.
        args: A list of string arguments to pass to the script.

    Returns:
        A formatted string containing the process output and status, or an error message string.
    """
    if args is None:
        args = []

    try:
        # 1. Calculate Full Absolute Paths
        abs_working_dir = os.path.abspath(working_directory)
        full_path = os.path.join(working_directory, file_path)
        abs_full_path = os.path.abspath(full_path)

        # 2. Guardrail Check: Ensure the target path is within the working directory
        if os.path.commonpath([abs_working_dir, abs_full_path]) != abs_working_dir:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        # 3. File existence and type checks
        if not os.path.exists(abs_full_path):
            return f'Error: File "{file_path}" not found.'
            
        if not file_path.lower().endswith(".py"):
            return f'Error: "{file_path}" is not a Python file.'

        # 4. Construct the command: ['python', 'full/path/to/script.py', 'arg1', 'arg2', ...]
        # Use sys.executable to ensure the correct Python interpreter is used (e.g., from uv).
        command = [sys.executable, abs_full_path] + args
        
        # 5. Execute the file using subprocess.run
        completed_process = subprocess.run(
            command,
            cwd=abs_working_dir, # Use the specified working directory for execution
            capture_output=True,
            text=True, # Decode stdout and stderr as strings
            timeout=30, # 30-second timeout
            check=False # Do not raise CalledProcessError for non-zero exit codes
        )

        stdout = completed_process.stdout.strip()
        stderr = completed_process.stderr.strip()
        exit_code = completed_process.returncode

        # 6. Format Output
        output = []
        
        # Check for output (stdout or stderr)
        if stdout or stderr:
            if stdout:
                output.append("STDOUT:\n" + stdout)
            if stderr:
                output.append("STDERR:\n" + stderr)
        else:
            # If no output and no non-zero exit code, return 'No output produced.'
            if exit_code == 0:
                return "No output produced."
            
        # 7. Include non-zero exit code message
        if exit_code != 0:
            output.append(f"Process exited with code {exit_code}")

        return "\n".join(output)

    except subprocess.TimeoutExpired:
        return f"Error: Python execution timed out after 30 seconds."
    except Exception as e:
        # Catch other potential exceptions 
        return f"Error: executing Python file: {e}"

# --- Function Declaration (Schema) for LLM Tool Calling ---

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python script with optional command-line arguments. Execution is limited to 30 seconds.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file to execute, relative to the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="An optional list of string arguments to pass to the Python script.",
                items=types.Schema(type=types.Type.STRING),
            ),
        },
        required=["file_path"],
    ),
)