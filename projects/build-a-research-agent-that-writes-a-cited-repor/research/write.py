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


def split_sentences(text):
    """
    Split a report into individual sentences while preserving
    citation markers.

    Rules:
    1. A sentence ends at '.', '?' or '!' when followed by
       whitespace or the end of the text.
    2. A newline also ends a sentence.
    3. Citation markers appearing after punctuation are moved
       immediately before the punctuation.
    4. Whitespace following citation markers is preserved.
    5. Empty pieces are discarded.
    """

    # Move citation markers after punctuation to before punctuation.
    # Importantly, do not consume whitespace following the markers.
    text = re.sub(
        r'([.!?])[ \t]*(\[\d+\](?:[ \t]+\[\d+\])*)',
        r' \2\1',
        text
    )

    # Split at sentence-ending punctuation followed by whitespace,
    # or at newline characters.
    # Decimal numbers such as 4.6 are not split because the
    # decimal point is not followed by whitespace.
    sentences = re.split(
        r'(?<=[.!?])\s+|\r?\n+',
        text
    )

    # Remove surrounding whitespace and discard empty sentences.
    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def markers(sentence):
    """
    Extract citation numbers from a sentence.

    Rules:
    1. Recognize square brackets containing one or more numbers.
    2. Support comma-separated numbers with or without spaces.
    3. Support multiple citation markers appearing side by side.
    4. Ignore brackets containing non-numeric content.
    5. Return unique citation numbers in their original order.

    Returns:
        A list of unique citation numbers as integers.
    """

    result = []
    seen = set()

    # Find valid citation markers such as [2], [1, 3], or [1,3].
    citation_groups = re.findall(
        r'\[(\s*\d+(?:\s*,\s*\d+)*\s*)\]',
        sentence
    )

    # Extract individual numbers from each citation marker.
    for group in citation_groups:
        for number in group.split(","):

            # Convert the citation number to an integer.
            number = int(number.strip())

            # Preserve order while removing duplicates.
            if number not in seen:
                result.append(number)
                seen.add(number)

    return result


def renumber(report):
    """
    Renumber citation markers according to their first appearance.

    Parameters:
        report: Report text containing numbered citation markers.

    Returns:
        A tuple containing:
        - text: Report with citation numbers renumbered.
        - mapping: Dictionary mapping old citation numbers
                   to their new 1-based citation numbers.

    Rules:
    1. Process citation markers from left to right.
    2. The first unique citation number becomes 1.
    3. Each subsequent new citation number receives the next number.
    4. Repeated citation numbers retain their assigned numbers.
    5. Preserve all text and formatting outside citation numbers.
    6. Reports without citations remain unchanged.
    """

    mapping = {}

    # Replace valid citation markers while preserving their formatting.
    def replace_marker(match):

        # Replace each number inside the citation marker.
        def replace_number(number_match):
            old_number = int(number_match.group())

            # Assign a new number on the first occurrence.
            if old_number not in mapping:
                mapping[old_number] = len(mapping) + 1

            return str(mapping[old_number])

        # Change only the numbers, preserving brackets,
        # commas, and whitespace.
        return re.sub(
            r'\d+',
            replace_number,
            match.group()
        )

    # Match numeric citation markers such as [3], [1, 3], and [3][1].
    text = re.sub(
        r'\[\s*\d+(?:\s*,\s*\d+)*\s*\]',
        replace_marker,
        report
    )

    return text, mapping
