def score_question(question, chunk):
    """
    Build a Jev score question to evaluate how well one passage
    answers the given question.
    """

    # Include both the question and passage text so Jev has
    # all the context needed to evaluate the passage independently.
    instructions = (
        f"How well does this passage answer the question? "
        f"Question: {question} "
        f"Passage: {chunk['text']}"
    )

    # Return the structured scoring request expected by Jev.
    # LEVELS is predefined and supplied by the project environment.
    return {
        "type": "score",
        "instructions": instructions,
        "criteria": LEVELS
    }


def in_batches(items, size):
    """
    Split a list of items into consecutive batches of at most
    the specified size.
    """

    # Ensure the batch size is valid.
    if size <= 0:
        raise ValueError("Batch size must be a positive integer.")

    # Create consecutive batches using list slicing.
    return [
        items[i:i + size]
        for i in range(0, len(items), size)
    ]
