import numpy as np
import torch


def embed_texts(texts, tokenizer, model):
    batch = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        output = model(**batch)

    mask = batch["attention_mask"].unsqueeze(-1).float()
    pooled = (output.last_hidden_state * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1e-9)

    # FIX 1: L2-normalize embeddings.
    pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)

    return pooled.cpu().numpy()


def chunk_all(documents, size=40, overlap=10):
    chunks = []
    for document in documents:
        words = document.split()
        step = size - overlap
        for start in range(0, len(words), step):
            piece = words[start:start + size]
            if piece:
                chunks.append(" ".join(piece))
            if start + size >= len(words):
                break
    return chunks


def retrieve(question, documents, tokenizer, model, k=3):
    chunks = chunk_all(documents)
    chunk_vectors = embed_texts(chunks, tokenizer, model)
    question_vector = embed_texts([question], tokenizer, model)[0]

    scores = chunk_vectors @ question_vector

    # FIX 2: Highest similarity first.
    ranked = np.argsort(-scores)

    results = []
    for position in ranked[:k]:
        # FIX 3: Use the exact chunk corresponding to the score.
        results.append((chunks[position], float(scores[position])))

    return results
