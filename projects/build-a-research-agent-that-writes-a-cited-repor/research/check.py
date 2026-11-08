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
    Verify whether a finding's quote appears in its original note.

    Source IDs are matched case-insensitively.
    Quote verification ignores case and whitespace differences only.
    """

    source_id = finding.get("source_id")
    quote = finding.get("quote")

    if not isinstance(quote, str) or not quote.strip():
        return False

    # Normalize the source ID.
    normalized_id = str(source_id).strip().upper()

    normalized_id = re.sub(
        r"^NOTE\s+",
        "",
        normalized_id,
        flags=re.IGNORECASE
    ).strip()

    # Normalize the quotation.
    normalized_quote = " ".join(
        quote.split()
    ).casefold()

    # Find the corresponding original document.
    for doc in docs:
        doc_id = str(doc.get("id", "")).strip().upper()

        doc_id = re.sub(
            r"^NOTE\s+",
            "",
            doc_id,
            flags=re.IGNORECASE
        ).strip()

        if doc_id != normalized_id:
            continue

        note_text = doc.get("text", "")

        if not isinstance(note_text, str):
            return False

        normalized_text = " ".join(
            note_text.split()
        ).casefold()

        return normalized_quote in normalized_text

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
