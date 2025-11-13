import os
from dotenv import load_dotenv
from google import genai
import sys
from google.genai import types
from functions.get_files_info import schema_get_files_info

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

# Define the available functions tool list
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
    ])

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
            # Print the function call
            print(f"Calling function: {function_call_part.name}({function_call_part.args})")
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
