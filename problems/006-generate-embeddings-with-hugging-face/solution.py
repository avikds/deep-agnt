import numpy as np
import torch

def embed(sentences, tokenizer, model):
    """Return normalized sentence embeddings, shape (n, d), as a NumPy array."""
    batch = tokenizer(
        sentences,
        padding=True,
        truncation=True,
        return_tensors="pt"
    )

    model.eval()
    with torch.no_grad():
        outputs = model(**batch)
        token_embeddings = outputs.last_hidden_state

        # Expand attention mask to match the embedding dimensions.
        mask = batch["attention_mask"].unsqueeze(-1).to(token_embeddings.dtype)

        # Masked mean pooling: exclude padding tokens.
        summed = (token_embeddings * mask).sum(dim=1)
        counts = mask.sum(dim=1).clamp(min=1)
        sentence_embeddings = summed / counts

        # L2-normalize each sentence embedding.
        sentence_embeddings = torch.nn.functional.normalize(
            sentence_embeddings, p=2, dim=1
        )

    return sentence_embeddings.cpu().numpy()
