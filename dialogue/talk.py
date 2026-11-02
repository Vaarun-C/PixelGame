from guard import clean_question, dont_know, reply_ok, suspicious
from prompt import VILLAGERS, messages, villager_prompt

MAX_HISTORY = 2


def pick(options, seed):
    return options[seed % len(options)]


def respond(body, generate):
    """body: the game's request; generate(messages) -> candidate replies. Returns the line to show."""
    if body.get("warm"):
        return ""
    v = VILLAGERS.get(body.get("role"))
    if not v:
        return "..."
    question = clean_question(body.get("question", ""))
    if not question or suspicious(question):
        return dont_know(v)
    wanderer = clean_question(body.get("wanderer", ""))
    seed = body.get("seed") if isinstance(body.get("seed"), int) else 0
    system = villager_prompt(
        v["role"],
        body.get("name", "Nobody"),
        body.get("village", "nowhere"),
        pick(v["moods"], seed),
        pick(v["losses"], seed // 7),
        body.get("dead", [])[:5],
        "" if suspicious(wanderer) else wanderer,
    )
    history = [
        (clean_question(q), a)
        for q, a in [h for h in body.get("history", []) if isinstance(h, list) and len(h) == 2 and all(isinstance(x, str) for x in h)][-MAX_HISTORY:]
        if not suspicious(clean_question(q)) and reply_ok(a, system)
    ]
    for reply in generate(messages(system, history, question)):
        reply = " ".join(reply.split())
        if reply_ok(reply, system):
            return reply
    return dont_know(v)
