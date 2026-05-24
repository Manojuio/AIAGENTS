import subprocess

def run_command(command:str)->str:
    """
   Safely executes local environmental workspace tests (e.g., 'npm test' or 'pytest').
    Captures both stdout and stderr logs cleanly.
    """
    try:
        banned = ["rm -rf", "rmdir", "mkfs", "shutdown", "del /f"]
        if any (token in command.lower() for token in banned):
            return "Error: Command contains potentially harmful operations and will not be executed."
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=20
        )
        output_log = f"---STDOUT---\n{result.stdout}\n"
        error_log = f"---STDERR---\n{result.stderr}\n" 
        exit_code = f"Exit Status Code: {result.returncode}\n  "
        return f"{output_log}{error_log}{exit_code}"
    except subprocess.TimeoutExpired:
        return "Error: Command execution timed out after 20 seconds."
    except Exception as e:
        return f"Error executing command: {str(e)}"