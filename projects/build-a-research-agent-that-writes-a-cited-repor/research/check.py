def uncited(report, n_sources):
    """
    Find report sentences that do not contain any valid citation.

    Parameters:
        report: Generated report text.
        n_sources: Total number of available sources.

    Returns:
        A list of sentences without valid citations,
        preserving their original order.

    Rules:
    1. Split the report into sentences using split_sentences().
    2. Extract citation numbers using markers().
    3. A citation is valid when 1 <= number <= n_sources.
    4. A sentence without any valid citation is considered uncited.
    5. Citations outside the valid range do not count.
    """

    uncited_sentences = []

    # Split the report into individual sentences.
    sentences = split_sentences(report)

    # Examine each sentence in its original order.
    for sentence in sentences:

        # Extract citation numbers from the sentence.
        citations = markers(sentence)

        # Check whether at least one citation is valid.
        has_valid_citation = any(
            1 <= number <= n_sources
            for number in citations
        )

        # Keep sentences without a valid citation.
        if not has_valid_citation:
            uncited_sentences.append(sentence)

    return uncited_sentences


def supported(finding, docs):
    """
    Verify whether a finding's quote exists in its original source note.

    Parameters:
        finding: Dictionary containing:
            - source_id: ID of the source document.
            - quote: Exact quotation to verify.

        docs: List of company documents containing:
            - id: Unique document identifier.
            - text: Original document text.

    Returns:
        True if the quote appears in the text of the matching
        source document, otherwise False.

    Verification rules:
    1. Find the document matching the finding's source_id.
    2. Return False if no matching document exists.
    3. Return False if the quote is empty.
    4. Collapse whitespace into single spaces.
    5. Ignore uppercase and lowercase differences.
    6. Check whether the normalized quote appears in the
       normalized document text.
    """

    # Retrieve the source ID and quotation.
    source_id = finding.get("source_id")
    quote = finding.get("quote")

    # An empty or non-string quotation is not valid evidence.
    if not isinstance(quote, str) or not quote.strip():
        return False

    # Normalize the quotation:
    # collapse whitespace and ignore case.
    normalized_quote = " ".join(quote.split()).casefold()

    # Search for the matching source document.
    for doc in docs:

        if not isinstance(doc, dict):
            continue

        # Match the source ID to the document ID.
        if doc.get("id") != source_id:
            continue

        # Retrieve the original note text.
        note_text = doc.get("text", "")

        if not isinstance(note_text, str):
            continue

        # Normalize the original note using the same rules.
        normalized_text = " ".join(note_text.split()).casefold()

        # Check whether the complete quotation exists in the note.
        if normalized_quote in normalized_text:
            return True

    # No matching source or quotation was found.
    return False


def report_card(report, findings, docs):
    """
    Evaluate a research report for citation coverage
    and supporting evidence.

    Parameters:
        report: Generated report text.
        findings: List of research findings containing
                  claim, source_id, and quote.
        docs: Original company documents.

    Returns:
        A dictionary containing:
        - sentences: Total number of report sentences.
        - cited: Number of sentences with valid citations.
        - uncited: Sentences without valid citations.
        - unsupported: Claims whose quotations are not
                       supported by their original source notes.
    """

    # Step 1: Split the report into individual sentences.
    sentences = split_sentences(report)

    # Step 2: Determine the number of unique sources.
    order, numbers = number_sources(findings)
    n_sources = len(order)

    # Step 3: Find sentences without valid citations.
    uncited_sentences = uncited(
        report,
        n_sources
    )

    # Step 4: Count sentences containing valid citations.
    cited_count = len(sentences) - len(uncited_sentences)

    # Step 5: Check every finding against its original source.
    # Keep the claims whose quotations are not supported.
    unsupported_claims = [
        finding["claim"]
        for finding in findings
        if not supported(finding, docs)
    ]

    # Step 6: Return the complete report assessment.
    return {
        "sentences": len(sentences),
        "cited": cited_count,
        "uncited": uncited_sentences,
        "unsupported": unsupported_claims
    }
