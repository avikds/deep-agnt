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
