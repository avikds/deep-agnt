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


def dedupe_questions(questions, threshold=0.8):
    """
    Remove near-duplicate research questions using Jaccard similarity.

    Two questions are considered near-duplicates when the Jaccard
    similarity of their token sets is greater than or equal to
    the specified threshold.

    Rules:
    1. Tokenize each question using the existing tokenize() function.
    2. Convert tokens into sets to remove repeated terms.
    3. Compare each question against previously retained questions.
    4. Keep the first question from each near-duplicate group.
    5. Two empty token sets are considered duplicates.

    Parameters:
        questions: List of research questions.
        threshold: Minimum Jaccard similarity for considering
                   two questions duplicates (default 0.8).

    Returns:
        A list of questions with near-duplicates removed,
        preserving their original order.
    """

    kept = []
    kept_sets = []

    # Process questions in their original order.
    for question in questions:

        # Convert the question into a set of search terms.
        terms = set(tokenize(question))

        # Check against previously retained questions only.
        is_duplicate = False

        for existing_terms in kept_sets:

            # Two empty sets are considered duplicates.
            if not terms and not existing_terms:
                is_duplicate = True
                break

            # Calculate Jaccard similarity.
            union = terms | existing_terms
            intersection = terms & existing_terms

            similarity = len(intersection) / len(union)

            # Reject the question if similarity meets the threshold.
            if similarity >= threshold:
                is_duplicate = True
                break

        # Retain only questions that are not near-duplicates.
        if not is_duplicate:
            kept.append(question)
            kept_sets.append(terms)

    return kept


def plan(question, model, limit=3):
    """
    Ask a real model to divide a research question into
    focused sub-questions that can be answered using
    company notes.

    Parameters:
        question: The original research question.
        model: Model object providing the chat() method.
        limit: Maximum number of sub-questions to return.

    Returns:
        A list of unique, clean research sub-questions.
    """

    # Define instructions for the research planner.
    system = (
        "You are a research planning assistant. "
        "Your task is to break a research question into "
        "focused, specific, and independently answerable "
        "sub-questions that can be investigated using "
        "a company's notes. "
        "Keep the questions relevant to the original question. "
        "Avoid asking overlapping or duplicate questions. "
        "Do not answer the questions or invent facts. "
        "Return only the sub-questions, with exactly one "
        "question per line. Do not include numbering, "
        "bullet points, headings, explanations, or any "
        "other text."
    )

    # Construct the prompt for the model.
    prompt = (
        f"Research question: {question}\n\n"
        f"Generate at most {limit} distinct sub-questions "
        "that together cover the important aspects of "
        "the research question.\n\n"
        "Return one sub-question per line and nothing else."
    )

    # Prepare the conversation messages.
    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    # Make one call to the model.
    reply = model.chat(
        messages,
        [],
        system,
        500
    )

    # Extract text from the model's response.
    text = reply_text(reply)

    # Parse the response into individual questions.
    questions = parse_lines(text)

    # Remove near-duplicate questions.
    questions = dedupe_questions(questions)

    # Return at most the requested number of questions.
    return questions[:max(0, limit)]
