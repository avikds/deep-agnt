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
