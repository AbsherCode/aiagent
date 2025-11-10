import os
import os.path
from typing import Optional

# We assume that config.py is importable from the environment path
# (e.g., if the project root is added to sys.path, as done in tests.py)
try:
    import config
    MAX_CHARS = config.MAX_CHARS
except ImportError:
    # Fallback if config.py isn't found, necessary for robust testing/running
    MAX_CHARS = 10000 


def get_file_content(working_directory: str, file_path: str) -> str:
    """
    Reads the content of a file within the restricted working directory, 
    with a character limit guardrail.
    
    Args:
        working_directory: The root directory the LLM is allowed to access.
        file_path: The relative path to the file.
        
    Returns:
        The truncated file content as a string, or an error message string.
    """
    try:
        # 1. Calculate Full Absolute Paths
        abs_working_dir = os.path.abspath(working_directory)
        full_path = os.path.join(working_directory, file_path)
        abs_full_path = os.path.abspath(full_path)

        # 2. Guardrail Check: Ensure the target path is within the working directory
        if os.path.commonpath([abs_working_dir, abs_full_path]) != abs_working_dir:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        # 3. File Check
        if not os.path.isfile(abs_full_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        # 4. Read and Truncate Content
        with open(abs_full_path, "r", encoding="utf-8") as f:
            # Read MAX_CHARS plus one extra character to detect truncation requirement
            content = f.read(MAX_CHARS + 1)

        is_truncated = len(content) > MAX_CHARS
        
        if is_truncated:
            # Truncate to the actual MAX_CHARS and append the message
            content = content[:MAX_CHARS]
            content += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
            
        return content

    except Exception as e:
        # Catch any unexpected I/O or OS errors and return a string description
        return f"Error: An unexpected error occurred while reading the file: {e}"
