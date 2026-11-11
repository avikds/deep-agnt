def answer(question):
    """Answer a question that may need two searches. Returns {"answer", "sources"}."""

    # First retrieval
    notes = retrieve(question)

    # Track every source once, preserving first-seen order
    all_notes = []
    seen = set()

    def add_notes(new_notes):
        for note in new_notes:
            if note["id"] not in seen:
                seen.add(note["id"])
                all_notes.append(note)

    add_notes(notes)

    # Ask what information is still missing
    context = "\n".join(
        f"[{note['id']}] {note['text']}" for note in all_notes
    )

    search_prompt = (
        f"Question: {question}\n\n"
        f"Retrieved notes:\n{context}\n\n"
        "Determine whether these notes contain enough information to answer "
        "the question. If they do, reply with exactly DONE. Otherwise, reply "
        "with one concise search query for the missing fact. "
        "Do not answer the original question."
    )

    follow_up = (llm.ask(search_prompt, max_tokens=60) or "").strip()

    # Perform at most one follow-up retrieval
    if follow_up and follow_up.upper().strip(" \n.!") != "DONE":
        add_notes(retrieve(follow_up))

    # Generate the final answer from all retrieved notes
    context = "\n".join(
        f"[{note['id']}] {note['text']}" for note in all_notes
    )

    final_prompt = (
        f"Question: {question}\n\n"
        f"Notes:\n{context}\n\n"
        "Answer the question using only the notes above. "
        "Give one short, direct sentence."
    )

    reply = llm.ask(final_prompt, max_tokens=60)

    return {
        "answer": (reply or "").strip(),
        "sources": [note["id"] for note in all_notes]
    }
