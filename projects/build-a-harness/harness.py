def tool_spec(name, description, properties=None, required=None):
    """
    Create a tool specification in the format expected by the model.
    """
    return {
        "name": name,
        "description": description,
        "input_schema": {
            "type": "object",
            "properties": dict(properties) if properties is not None else {},
            "required": list(required) if required is not None else []
        }
    }


def tool_specs():
    """
    Define the five tools available to the coding agent.
    Each tool parameter is a required string.
    """
    return [
        tool_spec(
            "list_files",
            "List all files in the project workspace."
        ),
        tool_spec(
            "read_file",
            "Read and return the contents of the specified file.",
            properties={
                "path": {"type": "string"}
            },
            required=["path"]
        ),
        tool_spec(
            "write_file",
            "Write the complete contents of a file in one operation. "
            "Never modify files inside tests/.",
            properties={
                "path": {"type": "string"},
                "content": {"type": "string"}
            },
            required=["path", "content"]
        ),
        tool_spec(
            "grep",
            "Search project files for a specified text pattern.",
            properties={
                "pattern": {"type": "string"}
            },
            required=["pattern"]
        ),
        tool_spec(
            "run_tests",
            "Run the project's test suite and return the results."
        )
    ]
