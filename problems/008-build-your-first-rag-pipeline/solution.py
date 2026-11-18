import numpy as np

def answer(question, documents, model, k=3):
    # 1. Chunk every document
    chunks = []
    for doc in documents:
        chunks.extend(chunk_document(doc, 40, 10))

    if not chunks:
        prompt = (
            "Answer the question using the provided context.\n\n"
            "Context:\n\n"
            "Question: " + question
        )
        return model.ask(prompt)

    # 2. Embed chunks and question together
    texts = chunks + [question]
    embeddings = np.asarray(embed(texts), dtype=np.float64)

    # 3. Cosine similarity
    norms = np.linalg.norm(embeddings, axis=1)
    norms = np.maximum(norms, 1e-12)

    chunk_embeddings = embeddings[:-1]
    question_embedding = embeddings[-1]

    similarities = (
        chunk_embeddings @ question_embedding
    ) / (norms[:-1] * norms[-1])

    # 4. Retrieve top k, preserving descending similarity order
    k = max(0, min(int(k), len(chunks)))

    if k:
        indices = np.argpartition(similarities, len(chunks) - k)[-k:]
        indices = indices[np.argsort(similarities[indices])[::-1]]
        context = "\n\n".join(chunks[i] for i in indices)
    else:
        context = ""

    # 5. Build prompt and query model
    prompt = (
        "Answer the question using the context below. "
        "If the context does not contain the answer, say so.\n\n"
        "Context:\n"
        + context
        + "\n\nQuestion:\n"
        + question
    )

    return model.ask(prompt)
