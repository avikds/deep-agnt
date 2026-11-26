import re

def judge(llm, question, answer):
    """Evaluate an answer using an explicit 1-to-5 rubric."""

    prompt = f"""
You are an impartial and strict answer evaluator.

Evaluate the candidate answer against the question.

QUESTION:
{question}

CANDIDATE ANSWER:
{answer}

SCORING RUBRIC:

5 - Excellent:
Completely correct, accurate, relevant, and sufficiently detailed.
Answers all important parts of the question.

4 - Good:
Correct answer with minor omissions or small inaccuracies.
The main question is answered correctly.

3 - Partial:
Contains some correct information but misses important details,
or has a mixture of correct and incorrect claims.

2 - Poor:
Mostly incorrect, substantially incomplete, or misunderstands
the question.

1 - Useless:
Irrelevant, nonsensical, entirely incorrect, or does not answer
the question.

IMPORTANT RULES:
- Judge factual correctness, not writing style.
- Reward concise answers when they fully answer the question.
- Do not reward confident wording without correctness.
- Do not penalize an answer for being shorter than necessary
  if it is completely correct.
- Compare the answer directly against the question.
- Give a score from 1 through 5.

Return your evaluation in this format:

SCORE: <integer>
REASON: <brief explanation>
"""

    try:
        response = llm.ask(prompt)

        if isinstance(response, (int, float)):
            return max(1, min(5, int(response)))

        text = str(response).strip()

        # First look for an explicitly labeled score.
        patterns = [
            r'\bSCORE\s*[:=]\s*([1-5])\b',
            r'\bRATING\s*[:=]\s*([1-5])\b',
            r'\b([1-5])\s*(?:out\s+of|/)\s*5\b',
            r'\b(?:score|rating)\s+(?:is|of)\s+([1-5])\b',
            r'\b(?:give|assign|rate)\w*\s+(?:it\s+)?(?:a\s+)?([1-5])\b',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return max(1, min(5, int(match.group(1))))

        # Handle responses consisting of a single digit.
        match = re.fullmatch(r'\s*([1-5])\s*[.!]?\s*', text)

        if match:
            return int(match.group(1))

        # Last resort: extract the first standalone valid digit.
        match = re.search(r'\b([1-5])\b', text)

        if match:
            return int(match.group(1))

        return 1

    except Exception:
        return 1
