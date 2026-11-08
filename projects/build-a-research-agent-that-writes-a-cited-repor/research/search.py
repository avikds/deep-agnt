def stem(word):
    """
    Reduce a lowercase word to a rough stem.

    Rules:
    1. Try removing 'ing', 'ed', 'es', or 's', in that order.
       Remove the first matching suffix only if at least three
       letters remain.
    2. If the resulting word ends in 'e', remove that 'e'.
    3. Otherwise, return the word unchanged.
    """

    # Remove the first eligible suffix.
    for suffix in ("ing", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            word = word[:-len(suffix)]
            break

    # Remove a trailing 'e', if present.
    if word.endswith("e"):
        word = word[:-1]

    return word
