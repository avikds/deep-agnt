def format_chat(messages):
    """Format conversation and prepare the assistant generation prompt."""

    if getattr(tokenizer, "chat_template", None) is not None:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

    return "\n".join(
        f"{message['role']}: {message['content']}"
        for message in messages
    )


def format_for_training(messages):
    """Format the complete conversation for training."""

    if getattr(tokenizer, "chat_template", None) is not None:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False
        )

    return "\n".join(
        f"{message['role']}: {message['content']}"
        for message in messages
    )
