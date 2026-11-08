from agentkit import ToolError


def run_with_approval(question, model, tools, destructive, approve, max_turns=6):
    """The standard tool loop, with a human gate on destructive calls."""
    messages = [{"role": "user", "content": question}]
    turns = 0
    approvals = []

    for _ in range(max_turns):
        response = model.messages.create(
            messages=messages,
            tools=tools.specs(),
            max_tokens=200
        )
        turns += 1

        messages.append({
            "role": "assistant",
            "content": [b.to_dict() for b in response.content]
        })

        if response.stop_reason != "tool_use":
            return {
                "answer": response.text,
                "turns": turns,
                "stopped": "done",
                "approvals": approvals
            }

        results = []

        for call in response.tool_calls:
            # Ask for approval before executing destructive tools.
            if call.name in destructive:
                approved = bool(approve(call.name, call.input))
                approvals.append((call.name, approved))

                if not approved:
                    return {
                        "answer": None,
                        "turns": turns,
                        "stopped": "denied",
                        "approvals": approvals
                    }

            # Execute the tool only after approval, if required.
            try:
                content = tools.call(call.name, call.input)
                is_error = False
            except ToolError as error:
                content = str(error)
                is_error = True

            results.append({
                "type": "tool_result",
                "tool_use_id": call.id,
                "content": content,
                "is_error": is_error
            })

        messages.append({
            "role": "user",
            "content": results
        })

    return {
        "answer": None,
        "turns": turns,
        "stopped": "turns",
        "approvals": approvals
    }
