def reply_text(reply):
    """
    Extract and combine all text blocks from a model reply.

    Parameters:
        reply: A dictionary returned by model.chat(), containing
               stop_reason, content, and usage.

    Returns:
        A single string containing all text blocks,
        joined without separators and stripped of
        leading and trailing whitespace.

    Non-text content blocks are ignored.
    """

    # Get the content blocks from the reply.
    content = reply.get("content", []) or []

    # Collect text from blocks whose type is "text".
    text_blocks = [
        block["text"]
        for block in content
        if isinstance(block, dict)
        and block.get("type") == "text"
        and isinstance(block.get("text"), str)
    ]

    # Join all text blocks without separators and trim whitespace.
    return "".join(text_blocks).strip()
