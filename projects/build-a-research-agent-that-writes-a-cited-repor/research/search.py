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


import re

if "STOPWORDS" not in globals():
    STOPWORDS = {
        "a", "an", "the", "and", "or", "but",
        "if", "in", "on", "at", "to", "for",
        "of", "by", "with", "as", "from",
        "is", "are", "was", "were", "be",
        "been", "being", "it", "its", "this",
        "that", "these", "those", "he", "she",
        "they", "them", "we", "you", "i",
        "my", "your", "our", "their", "his",
        "her", "do", "does", "did", "have",
        "has", "had", "can", "could", "would",
        "should", "will", "what", "which",
        "who", "whom", "when", "where", "why",
        "how"
    }


def tokenize(text):
    """
    Convert text into an ordered list of search terms.

    1. Convert the text to lowercase.
    2. Extract runs of letters and digits.
    3. Remove stopwords and words shorter than two characters.
    4. Apply the stem() function to each remaining word.
    5. Preserve repeated words and their original order.
    """

    # Extract lowercase words containing letters and digits.
    words = re.findall(r"[a-z0-9]+", text.lower())

    # Filter stopwords and short words, then stem the remaining words.
    tokens = [
        stem(word)
        for word in words
        if len(word) >= 2 and word not in STOPWORDS
    ]

    return tokens
