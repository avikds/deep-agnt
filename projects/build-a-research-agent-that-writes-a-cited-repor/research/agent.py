def revise(question, report, bad, findings, numbers, model):
    """
    Ask the model to revise sentences that failed report verification.

    Parameters:
        question: Original research question.
        report: Complete original report.
        bad: List of sentences that need correction.
        findings: List of validated research findings.
        numbers: Dictionary mapping source IDs to citation numbers.
        model: Model object providing the chat() method.

    Returns:
        The complete revised report as a string.

    Rules:
    1. Make exactly one call to model.chat().
    2. Include the question, numbered findings, original report,
       and sentences requiring correction in the prompt.
    3. Rewrite each bad sentence using only supporting findings.
    4. Remove sentences that have no supporting finding.
    5. Preserve all other sentences unchanged.
    6. Return the original report if the model response is empty.
    """

    # Step 1: Format all research findings with their citation numbers.
    finding_lines = []

    for finding in findings:
        source_id = finding["source_id"]
        citation_number = numbers[source_id]

        claim = finding["claim"]
        quote = finding["quote"]

        finding_lines.append(
            f'[{citation_number}] {claim} (quote: "{quote}")'
        )

    evidence = "\n".join(finding_lines)

    # Step 2: Format the sentences that need correction.
    bad_sentences = "\n".join(
        f"- {sentence}"
        for sentence in bad
    )

    # Step 3: Construct the revision prompt.
    prompt = (
        "ORIGINAL RESEARCH QUESTION:\n"
        f"{question}\n\n"

        "AVAILABLE RESEARCH FINDINGS:\n"
        f"{evidence}\n\n"

        "ORIGINAL REPORT:\n"
        f"{report}\n\n"

        "SENTENCES THAT NEED FIXING:\n"
        f"{bad_sentences}\n\n"

        "REVISION INSTRUCTIONS:\n"
        "Rewrite each listed sentence so that it ends with the "
        "citation number of a finding that genuinely supports it. "
        "Place citation numbers in square brackets immediately "
        "before the final full stop.\n\n"

        "Use only the research findings provided above. "
        "Do not invent claims, facts, quotations, or citations.\n\n"

        "If no finding supports a listed sentence, remove that "
        "sentence completely rather than making an unsupported claim.\n\n"

        "Leave all sentences that are not listed for correction "
        "exactly as they are.\n\n"

        "Preserve the original report's meaning and wording wherever "
        "possible. Use the supplied citation numbers exactly as provided.\n\n"

        "Return the complete revised report, including all unchanged "
        "sentences. Do not return only the corrected sentences.\n\n"

        "Return nothing except the revised report. "
        "Do not include headings, explanations, or commentary."
    )

    # Step 4: Ask the model to revise the report in one call.
    reply = model.chat(
        [
            {
                "role": "user",
                "content": prompt
            }
        ],
        [],
        (
            "You are a careful research report editor. "
            "Correct unsupported or uncited sentences using "
            "only the supplied research findings. "
            "Preserve valid sentences exactly. "
            "Never invent evidence or citations."
        ),
        1500
    )

    # Step 5: Extract the revised report.
    revised_report = reply_text(reply)

    # If the model returns no text, preserve the original report.
    if not revised_report:
        return report

    return revised_report
