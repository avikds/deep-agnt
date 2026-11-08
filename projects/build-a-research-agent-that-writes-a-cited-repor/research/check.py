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
