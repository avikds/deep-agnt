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


def format_tests(result):
    """
    Format test results with the summary on the first line
    and each failure indented by two spaces on separate lines.
    """
    summary = result["summary"]
    failures = result.get("failures", [])

    if not failures:
        return summary

    return "\n".join(
        [summary] + [f"  {failure}" for failure in failures]
    )


def run_tool(workspace, name, arguments):
    """
    Execute the requested tool on the workspace
    and return its result as a string.
    """

    if name == "list_files":
        return "\n".join(workspace.list())

    elif name == "read_file":
        return workspace.read(arguments["path"])

    elif name == "write_file":
        return workspace.write(
            arguments["path"],
            arguments["content"]
        )

    elif name == "grep":
        matches = workspace.grep(arguments["pattern"])
        return "\n".join(matches) if matches else "(no matches)"

    elif name == "run_tests":
        return format_tests(workspace.run_tests())

    else:
        raise ValueError(
            f"unknown tool '{name}'; the tools are "
            "list_files, read_file, write_file, grep, run_tests"
        )
