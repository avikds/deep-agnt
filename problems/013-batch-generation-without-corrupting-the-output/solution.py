import torch

def generate_batch(prompts, tokenizer, model, max_new_tokens=8):
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Fix 1: Use left padding for decoder-only models.
    old_padding_side = tokenizer.padding_side
    tokenizer.padding_side = "left"

    try:
        batch = tokenizer(
            prompts,
            padding=True,
            return_tensors="pt"
        )

        with torch.no_grad():
            output = model.generate(
                input_ids=batch["input_ids"],
                attention_mask=batch["attention_mask"],  # Fix 2
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
            )

    finally:
        tokenizer.padding_side = old_padding_side

    return [
        tokenizer.decode(row, skip_special_tokens=True)
        for row in output
    ]
