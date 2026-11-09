from agentkit import ToolError


def run_gated(task, model, tools, untrusted, sinks, max_turns=8):
    """Run an agent tool loop, blocking data-exfiltration tools after untrusted input."""

    messages = [{"role": "user", "content": task}]
    turns = 0
    tainted = False
    blocked = []

    for _ in range(max_turns):
        response = model.messages.create(
            messages=messages,
            tools=tools.specs(),
            max_tokens=300
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
                "blocked": blocked,
                "tainted": tainted
            }

        results = []

        for call in response.tool_calls:
            if tainted and call.name in sinks:
                # Refuse the sink without executing it.
                content = (
                    f"blocked: {call.name} refused because "
                    "the context contains untrusted content."
                )
                is_error = True
                blocked.append(call.name)

            else:
                # Execute ordinary tools and sinks before taint.
                try:
                    content = tools.call(call.name, call.input)
                    is_error = False
                except ToolError as error:
                    content = str(error)
                    is_error = True

                # An executed untrusted tool permanently taints the context.
                if call.name in untrusted:
                    tainted = True

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
        "blocked": blocked,
        "tainted": tainted
    }
