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
