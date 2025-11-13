import os
import os.path
from google.genai import types

def write_file(working_directory: str, file_path: str, content: str) -> str:
    """
    Writes content to a file within the restricted working directory, 
    creating the file if it does not exist, or overwriting it if it does.
    
    Args:
        working_directory: The root directory the LLM is allowed to access.
        file_path: The relative path to the file.
        content: The string content to write to the file.
        
    Returns:
        A success string confirming the write operation, or an error message string.
    """
    try:
        # 1. Calculate Full Absolute Paths
        abs_working_dir = os.path.abspath(working_directory)
        full_path = os.path.join(working_directory, file_path)
        abs_full_path = os.path.abspath(full_path)

        # 2. Guardrail Check: Ensure the target path is within the working directory
        # The common path between the two must be exactly the working directory itself.
        if os.path.commonpath([abs_working_dir, abs_full_path]) != abs_working_dir:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

        # 3. Ensure the parent directory exists
        parent_dir = os.path.dirname(abs_full_path)
        if not os.path.isdir(parent_dir):
            # This handles creating the subdirectory structure if necessary
            os.makedirs(parent_dir, exist_ok=True)
            
        # 4. Write the content, overwriting any existing data
        # Using 'w' mode ensures the file is created if it doesn't exist, 
        # or truncated and overwritten if it does.
        with open(abs_full_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        # 5. Return success string
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

    except Exception as e:
        # Catch any unexpected I/O or OS errors and return a string description
        return f"Error: An unexpected error occurred while writing the file: {e}"
    
# --- Function Declaration (Schema) for LLM Tool Calling ---

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a file within the restricted working directory, creating the file if it does not exist, or overwriting it if it does.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to write to, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The complete string content to be written to the file.",
            ),
        },
        required=["file_path", "content"],
    ),
)
