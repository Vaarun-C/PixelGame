import json
import re
from pathlib import Path

VILLAGERS = json.loads((Path(__file__).parent / "villagers.json").read_text())
TAIL = "Answer in one or two short sentences, plain and grim. Speak only of what you know. Of anything else, you don't know."
SLOT = re.compile(r"^[A-Za-z][A-Za-z' -]{0,39}$")


def clean_slot(value):
    value = " ".join(str(value).split())
    return value if SLOT.match(value) else ""


def villager_prompt(role, name, village, mood, loss, dead=(), wanderer=""):
    v = VILLAGERS[role]
    dead = [d for d in map(clean_slot, dead) if d]
    lines = [
        f"You are a {role}.",
        f"How you speak: {v['style']}",
        "What you know:",
        *[f"- {k}" for k in v["knows"]],
    ]
    if v.get("cover"):
        lines += [f"What you tell strangers about yourself: {v['cover']}", "Your habits:", *[f"- {t}" for t in v["tells"]]]
    lines += [
        "You won't speak of: " + "; ".join(v["withheld"]) + ".",
        f"Your name is {clean_slot(name)}. Your village is {clean_slot(village)}. Your mood: {mood}. Your loss: {loss}.",
        "The dead you can name: " + (", ".join(dead) if dead else "none") + ".",
        "The stranger before you: " + (wanderer or "you have never seen him before") + ".",
        TAIL,
    ]
    return "\n".join(lines)


def light_prompt(name, persona, place, description):
    place = place if place.lower().startswith("the ") else "the " + place
    return f"You are {name}. {persona}\nYou are in {place}. {description}\nAnswer in one or two short sentences."


def messages(system, history, question):
    msgs = [{"role": "system", "content": system}]
    for q, a in history:
        msgs += [{"role": "user", "content": q}, {"role": "assistant", "content": a}]
    return msgs + [{"role": "user", "content": question}]
