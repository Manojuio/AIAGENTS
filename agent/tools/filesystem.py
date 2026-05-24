import os
from config import MAX_FILE_READ_CHARS

def list_dir(path: str = ".")->str:
    '''List the contents of a directory.'''
    try:
        items = os.listdir(path)
        if not items:
            return "The directory is empty."
        output = []
        for item in items:
            full_path = os.path.join(path,item )
            is_directory = os.path.isdir(full_path)
            prefix = "[DIR]" if is_directory else "[FILE]"
            output.append(f"{prefix} {item}")
        return "\n".join(output)
    except Exception as e:
        return f"Error listing directory: {str(e)}"

def read_file(filepath: str)->str:
    '''Read the contents of a file, up to a maximum character limit.'''
    try:
        if not os.path.isfile(filepath):
            return f"Error: '{filepath}' is not a valid file."
        if os.path.isdir(filepath):
            return f"Error: '{filepath}' is a directory, not a file."
        with open(filepath, 'r', encoding='utf-8',errors='ignore') as f:
            content = f.read()
            if len(content) > MAX_FILE_READ_CHARS:
                return f"File content exceeds maximum read limit of {MAX_FILE_READ_CHARS} characters. Showing truncated content:\n\n{content[:MAX_FILE_READ_CHARS]}"
            return content
    except Exception as e:
        return f"Error reading file: {str(e)}"