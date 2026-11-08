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


def parse_lines(text):
    """
    Parse a model-generated list into clean strings.

    Processing:
    1. Split the response into individual lines.
    2. Strip whitespace from each line.
    3. Remove leading numbering or bullet markers.
    4. Remove Markdown bold markers and surrounding quotes.
    5. Remove empty lines.
    6. Remove exact duplicate items while preserving order.

    Returns:
        A list of clean strings.
    """

    items = []
    seen = set()

    # Process each line separately.
    for line in text.splitlines():

        # Remove leading and trailing whitespace.
        line = line.strip()

        # Skip empty lines.
        if not line:
            continue

        # Remove numbering such as 1. or 2),
        # and bullet markers such as - or *.
        line = re.sub(r"^(?:\d+[.)]|[-*])\s+", "", line)

        # Remove Markdown bold markers and surrounding quotes.
        line = line.strip('*"\'“”‘’').strip()

        # Skip lines that become empty after cleaning.
        if not line:
            continue

        # Remove exact duplicates while preserving original order.
        if line not in seen:
            items.append(line)
            seen.add(line)

    return items
