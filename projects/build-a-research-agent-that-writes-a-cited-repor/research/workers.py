def parse_findings(text, allowed):
    """
    Parse a researcher's pipe-separated findings.

    Expected format:
        claim | SOURCE_ID | "exact quote"

    Rules:
    1. Parse lines using the existing parse_lines() function.
    2. Split each line into exactly three parts using '|'.
    3. Strip whitespace from each part.
    4. Uppercase the source ID and remove a leading 'NOTE '.
    5. Remove surrounding quotation marks from the quote.
    6. Reject findings with unknown source IDs.
    7. Reject findings with empty claims or quotes.

    Parameters:
        text: Raw text returned by the researcher.
        allowed: Collection of permitted source IDs.

    Returns:
        A list of dictionaries containing:
        claim, source_id, and quote.
    """

    findings = []

    # Normalize allowed source IDs for case-insensitive validation.
    if isinstance(allowed, str):
        allowed = [allowed]

    allowed_ids = {
        re.sub(
            r"^NOTE\s+",
            "",
            str(source_id).strip(),
            flags=re.IGNORECASE
        ).upper()
        for source_id in (allowed or [])
    }

    # Parse the response into individual lines.
    lines = parse_lines(text)

    for line in lines:

        # Split each line into exactly three parts.
        parts = [part.strip() for part in line.split("|")]

        if len(parts) != 3:
            continue

        claim, source_id, quote = parts

        # Normalize the source ID.
        source_id = re.sub(
            r"^NOTE\s+",
            "",
            source_id,
            flags=re.IGNORECASE
        ).upper()

        # Remove surrounding quotation marks from the quote.
        quote = quote.strip('"\'“”‘’').strip()

        # Reject findings with missing claims or quotes.
        if not claim or not quote:
            continue

        # Reject findings referencing unauthorized sources.
        if source_id not in allowed_ids:
            continue

        # Store the validated finding.
        findings.append({
            "claim": claim,
            "source_id": source_id,
            "quote": quote
        })

    return findings


def worker_prompt(subquestion, hits, docs):
    """
    Build a research prompt containing a sub-question
    and only the company notes selected by search.

    Parameters:
        subquestion: Research question assigned to the worker.
        hits: Search results containing document IDs.
        docs: Complete collection of company documents.

    Returns:
        A formatted prompt containing:
        - The research sub-question.
        - The permitted notes with their IDs and titles.
        - The required findings output format.

    Notes whose IDs are not found in docs are skipped.
    """

    # Create a lookup dictionary for documents by ID.
    docs_by_id = {
        doc["id"]: doc
        for doc in docs
    }

    # Collect only the notes referenced by the search hits.
    note_blocks = []

    for hit in hits:

        # Get the document ID from the search result.
        doc_id = hit.get("id")

        # Skip hits without an ID or without a corresponding document.
        if not doc_id or doc_id not in docs_by_id:
            continue

        # Retrieve the original document.
        doc = docs_by_id[doc_id]

        # Include the note ID and title, followed by its full text.
        note_blocks.append(
            f"NOTE {doc_id}: {doc['title']}\n"
            f"{doc['text']}"
        )

    # Combine all permitted notes in their original hit order.
    notes = "\n\n".join(note_blocks)

    # Construct the researcher's instructions.
    prompt = (
        "You are a careful company research assistant.\n\n"

        "SUB-QUESTION:\n"
        f"{subquestion}\n\n"

        "PERMITTED SOURCE MATERIAL:\n"
        "You may use ONLY the notes provided below. "
        "Do not use outside knowledge, assumptions, or "
        "information from any other source. "
        "Every finding must be supported by one of these notes.\n\n"

        "NOTES:\n"
        f"{notes}\n\n"

        "OUTPUT REQUIREMENTS:\n"
        "Return one finding per line using exactly this format:\n"
        'claim | SOURCE_ID | "exact quote copied from the note"\n\n'

        "Provide at most four findings. "
        "The source ID must match the corresponding note ID. "
        "Every quote must be copied exactly from the note "
        "you are citing. Do not invent, paraphrase, or alter "
        "quotes.\n\n"

        "Return only the findings, one per line. "
        "Do not include headings, numbering, bullet points, "
        "introductions, explanations, or any other text."
    )

    return prompt


def research(subquestion, docs, model, k=4):
    """
    Run one research worker to answer a sub-question
    using relevant company notes.

    Parameters:
        subquestion: Research question assigned to the worker.
        docs: Complete collection of company documents.
        model: Model object providing the chat() method.
        k: Maximum number of notes to retrieve (default 4).

    Returns:
        A list of validated findings, each containing:
        - claim
        - source_id
        - quote

    Only sources returned by search() are permitted.
    """

    # Step 1: Retrieve the most relevant company notes.
    hits = search(docs, subquestion, k=k)

    # Step 2: Collect the IDs of the permitted source notes.
    allowed = {
        hit["id"]
        for hit in hits
    }

    # Step 3: Prepare the researcher's prompt.
    prompt = worker_prompt(
        subquestion,
        hits,
        docs
    )

    # Step 4: Send the research task to the model.
    # The researcher receives only the notes included in the prompt.
    reply = model.chat(
        [
            {
                "role": "user",
                "content": prompt
            }
        ],
        [],
        "You are a careful company research assistant. "
        "Follow the research instructions exactly. "
        "Use only the supplied notes and never invent "
        "claims or quotations.",
        800
    )

    # Step 5: Extract the textual response.
    response_text = reply_text(reply)

    # Step 6: Parse findings and reject unauthorized sources.
    findings = parse_findings(
        response_text,
        allowed
    )

    return findings


from concurrent.futures import ThreadPoolExecutor


def research_all(subquestions, docs, model, budget=4, workers=3):
    """
    Run research for multiple sub-questions under a budget.

    Parameters:
        subquestions: List of research sub-questions.
        docs: Complete collection of company documents.
        model: Model object providing the chat() method.
        budget: Maximum number of sub-questions to research.
        workers: Maximum number of parallel workers.

    Returns:
        A dictionary mapping each researched sub-question
        to its list of findings.

    Rules:
    1. Research only the first 'budget' sub-questions.
    2. Preserve the original sub-question order.
    3. Use ThreadPoolExecutor when workers > 1.
    4. Run sequentially when workers <= 1.
    5. Return [] when a researcher fails or returns nothing.
    6. One researcher's failure must not stop other researchers.
    """

    # Select only the sub-questions allowed by the budget.
    selected = list(subquestions)[:max(0, budget)]

    results = {}

    # Safely execute one research task.
    def run_one(subquestion):
        try:
            findings = research(
                subquestion,
                docs,
                model
            )

            # Normalize empty or missing findings.
            return findings if findings else []

        except Exception:
            # A failed researcher must not interrupt other workers.
            return []

    # Run research sequentially when only one worker is allowed.
    if workers <= 1:

        for subquestion in selected:
            results[subquestion] = run_one(subquestion)

    else:
        # Run multiple research tasks concurrently.
        # executor.map() preserves the original input order.
        with ThreadPoolExecutor(max_workers=workers) as executor:

            findings_list = list(
                executor.map(run_one, selected)
            )

        # Combine sub-questions and findings in their original order.
        for subquestion, findings in zip(selected, findings_list):
            results[subquestion] = findings

    return results
