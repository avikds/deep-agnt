def number_sources(findings):
    """
    Assign sequential citation numbers to source IDs.

    Parameters:
        findings: List of research findings, where each finding
                  contains a source_id.

    Returns:
        A tuple containing:
        - order: List of unique source IDs in first-appearance order.
        - numbers: Dictionary mapping each source ID to its
                   1-based citation number.

    Multiple findings from the same source share one number.
    An empty findings list returns ([], {}).
    """

    order = []
    numbers = {}

    # Process findings in their original order.
    for finding in findings:

        source_id = finding["source_id"]

        # Assign a number only when the source appears for the first time.
        if source_id not in numbers:
            order.append(source_id)
            numbers[source_id] = len(order)

    return order, numbers


def writer_prompt(question, findings, numbers):
    """
    Build a prompt for the report-writing model.

    Parameters:
        question: Original research question.
        findings: List of validated research findings.
        numbers: Dictionary mapping source IDs to citation numbers.

    Returns:
        A formatted prompt containing the research question,
        numbered findings, supporting quotes, and report instructions.
    """

    finding_lines = []

    # Format each finding using its assigned citation number.
    for finding in findings:
        source_id = finding["source_id"]
        citation_number = numbers[source_id]

        claim = finding["claim"]
        quote = finding["quote"]

        finding_lines.append(
            f'[{citation_number}] {claim} (quote: "{quote}")'
        )

    # Combine the findings, preserving their original order.
    evidence = "\n".join(finding_lines)

    # Construct the writer's prompt.
    prompt = (
        "RESEARCH QUESTION:\n"
        f"{question}\n\n"

        "AVAILABLE RESEARCH FINDINGS:\n"
        f"{evidence}\n\n"

        "REPORT WRITING INSTRUCTIONS:\n"
        "Write a report of three to six sentences that directly "
        "answers the research question using only the findings "
        "provided above.\n\n"

        "Every sentence must end with the citation number or "
        "numbers of the finding(s) it relies on, written in "
        "square brackets immediately before the final full stop.\n\n"

        "For example:\n"
        "The company recalled the Nova lantern due to overheating [2].\n"
        "The issue also affected the charging system [1][3].\n\n"

        "A sentence may cite several findings when appropriate. "
        "Use the supplied citation numbers exactly as provided. "
        "Do not introduce unsupported facts, external information, "
        "assumptions, or invented evidence.\n\n"

        "Return nothing but the report itself. "
        "Do not include a heading, introduction, explanation, "
        "bullet points, or a separate bibliography."
    )

    return prompt
