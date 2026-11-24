from collections import Counter

def consistent_answer(llm, question, samples=5):
    """Ask samples times and return the most common normalized answer."""

    answers = []

    for _ in range(samples):
        response = llm.ask(question)

        # Normalize the response.
        answer = response.strip().lower()

        # Remove one trailing period.
        if answer.endswith("."):
            answer = answer[:-1]

        answers.append(answer)

    # Return the most frequently occurring answer.
    return Counter(answers).most_common(1)[0][0]
