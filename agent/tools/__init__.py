from google.genai import types
from agent.tools.filesystem import list_dir, read_file
from agent.tools.terminal import run_command


TOOL_DECLARATIONS = [
    types.FunctionDeclaration(
        name="list_dir",
        description="Lists all file and directory names in a given folder pathway.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={"path": types.Schema(type=types.Type.STRING, description="Relative target path default is '.'")},
        )
    ),
    types.FunctionDeclaration(
        name="read_file",
        description="Reads raw text contents from a specific code file link.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={"filepath": types.Schema(type=types.Type.STRING, description="Path to the targeted script file")},
            required=["filepath"]
        )
    ),
    types.FunctionDeclaration(
        name="run_command",
        description="Runs isolated project checking commands like 'npm test', 'node server.js', or 'pytest' to view console error stack traces.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={"command": types.Schema(type=types.Type.STRING, description="The shell text command statement to execute")},
            required=["command"]
        )
    )
]

def execute_agent_tool(name:str,arguments:dict)->str:
    '''Centralized execution function for all agent tools.'''
    if name == "list_dir":
        target_path = arguments.get("path", ".")
        return list_dir(target_path)
    elif name == "read_file":
        filepath = arguments.get("filepath")
        return read_file(filepath)
    elif name == "run_command":
        command = arguments.get("command")
        return run_command(command)
    else:
        return f"Error: Tool '{name}' is not recognized or supported."