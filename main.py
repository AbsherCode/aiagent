import os
from dotenv import load_dotenv
from google import genai
import sys
from google.genai import types

# --- 1. Import all function schemas ---
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file
from functions.write_file import schema_write_file

# --- 2. Import actual Python functions ---
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python_file import run_python_file
from functions.write_file import write_file

# --- 3. Constants and Mappings ---
WORKING_DIRECTORY = "./calculator"
# Map function names (strings used in schema) to the actual callable functions
FUNCTION_MAP = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "write_file": write_file,
}

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

# Define the available functions tool list
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ])


def call_function(function_call_part: types.FunctionCall, verbose: bool = False) -> types.Content:
    """
    Handles the execution of a tool function based on the model's FunctionCall request.

    Args:
        function_call_part: The FunctionCall object from the model response.
        verbose: If True, prints detailed function call information.

    Returns:
        A types.Content object containing the function response.
    """
    function_name = function_call_part.name
    # Convert ImmutableDict to standard dict for modification
    function_args = dict(function_call_part.args) 
    
    # 1. Print function call information
    if verbose:
        print(f"Calling function: {function_name}({function_args})")
    else:
        # Check if function exists before printing simplified call
        if function_name in FUNCTION_MAP:
            print(f" - Calling function: {function_name}")
        else:
             # Handle invalid function name right away
            print(f" - Error: Unknown function '{function_name}'")


    # 2. Add the hardcoded working directory for security
    function_args['working_directory'] = WORKING_DIRECTORY

    # 3. Check for valid function and call it
    if function_name not in FUNCTION_MAP:
        # Invalid function name response
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    
    # Get the callable function
    func_to_call = FUNCTION_MAP[function_name]
    
    # Call the function with keyword arguments
    try:
        function_result = func_to_call(**function_args)
    except Exception as e:
        # Handle exceptions during function execution
        function_result = f"Error during execution of {function_name}: {e}"

    # 4. Return the result wrapped in a Content object
    # Note: The response must be a dictionary, so we wrap the string result in {"result": ...}
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )


def main():

    # Load environment variables from .env file
    load_dotenv()

    args = sys.argv[1:]
    
    is_verbose = "--verbose" in sys.argv[1:] 

    if not args:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here"')
        print('Example: python main.py "How do I build a calculator app?"')
        sys.exit(1)
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    client = genai.Client(api_key=api_key)
    
    user_prompt = " ".join(args)

    if is_verbose:
        print(f"User prompt: {user_prompt}\n") 

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    generate_content(client, messages, is_verbose)

def generate_content(client, messages, is_verbose=True):

    response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                tools=[available_functions],
            ),
    )
    # Print the .text property of the response
    print("--- Model Response ---")
    # Check for function calls first
    function_calls = response.function_calls
    if function_calls:
        for function_call_part in function_calls:
            # Execute the tool and get the result wrapped in Content
                function_call_result = call_function(function_call_part, is_verbose)
                
                # Check for the expected function response structure
                if (function_call_result.parts and 
                    function_call_result.parts[0].function_response and 
                    function_call_result.parts[0].function_response.response):
                    
                    # Print the result if verbose
                    if is_verbose:
                        # The result is a dictionary: {"result": "..."} or {"error": "..."}
                        result_data = function_call_result.parts[0].function_response.response
                        print(f"-> {result_data}") 
                        
                else:
                    # Raise an error if the structure is unexpected
                    raise RuntimeError(f"Expected function response part not found in result for {function_call_part.name}")

    else:
        # If no function calls, print the text response
        print(response.text)

    # Print the token usage metadata
    if is_verbose:
        print("\n--- Token Usage ---")
        usage = response.usage_metadata
        print(f"Prompt tokens: {usage.prompt_token_count}")
        print(f"Response tokens: {usage.candidates_token_count}")
    


if __name__ == "__main__":
    main()
