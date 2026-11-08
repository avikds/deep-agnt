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


def build_index(docs):
    """
    Build an inverted index from a collection of documents.

    The index maps:
        term -> document_id -> occurrence_count

    Each document is expected to contain:
        - id: The document's unique identifier.
        - text: The document's textual content.
    """

    index = {}

    # Process each document in the corpus.
    for doc in docs:
        doc_id = doc["id"]
        text = doc["text"]

        # Convert the document text into search terms.
        terms = tokenize(text)

        # Count each term's occurrences in this document.
        for term in terms:
            if term not in index:
                index[term] = {}

            index[term][doc_id] = index[term].get(doc_id, 0) + 1

    return index


import math


def score(index, n_docs, query):
    """
    Score documents based on their relevance to a search query.

    Each query term contributes:
        term_frequency * inverse_document_frequency

    IDF = log(1 + n_docs / df)

    where:
        n_docs = Total number of documents.
        df     = Number of documents containing the term.

    Returns:
        A dictionary mapping document IDs to scores rounded
        to three decimal places.
    """

    scores = {}

    # Convert the query into search terms.
    query_terms = tokenize(query)

    # Process every query term, including repeated terms.
    for term in query_terms:

        # Ignore terms that do not exist in the index.
        if term not in index:
            continue

        # Get the documents containing this term.
        postings = index[term]

        # Calculate document frequency.
        df = len(postings)

        # Avoid division by zero for an empty posting list.
        if df == 0:
            continue

        # Calculate inverse document frequency.
        idf = math.log(1 + n_docs / df)

        # Add this term's contribution to each document's score.
        for doc_id, count in postings.items():
            scores[doc_id] = scores.get(doc_id, 0) + count * idf

    # Round final scores to three decimal places.
    return {
        doc_id: round(value, 3)
        for doc_id, value in scores.items()
    }
