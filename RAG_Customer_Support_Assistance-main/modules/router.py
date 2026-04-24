def route(query, docs, answer):
    if not docs:
        return "escalate"

    if len(answer.strip()) < 40:
        return "escalate"

    if "I don't know" in answer or "not available" in answer:
        return "escalate"

    return "answer"