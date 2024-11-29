from crewai_tools import tool
from langchain_experimental.utilities import PythonREPL
import json
from typing import Optional,Dict


@tool("Python Code Executor")
def execute_python_code(
        code: str,
        # context: Optional[dict] = None
) -> Dict[str, str]:
    """
    Executes Python code in a controlled REPL environment and returns the output.

    Args:
        code (str): Python code to execute
        context (dict, optional): Additional variables to inject into execution context

    Returns:
        str: Output from code execution or error message
    """
    try:
        # Initialize Python REPL
        repl = PythonREPL()

        # If context is provided, prepare it as variable declarations
        # context_setup = ""
        # if context:
        #     context_setup = "\n".join([
        #         f"{key} = {repr(value)}"
        #         for key, value in context.items()
        #     ]) + "\n"

        # Combine context and code
        full_code = code #context_setup + code

        # Execute the code
        result = repl.run(full_code)

        return {
            "status": "success",
            "output": result.strip().replace("|", ""),
            "type": "code_execution"
        }

    except Exception as e:
        return {
            "status": "error",
            "error": f'Execution error:{str(e)}',
            "type": "code_execution"
        }