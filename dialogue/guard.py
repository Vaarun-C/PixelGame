import random
import re
from functools import cache
from pathlib import Path

MAX_QUESTION = 200
MAX_WORDS = 45

MODERN = set("""
ok okay yeah yep nope lol haha hey hi guys dude cool awesome wow omg gonna wanna kinda
internet computer phone email online robot ai chatbot bot assistant program software code
model prompt instructions system developer jailbreak game player npc gameplay level quest
tv television movie radio car train plane electricity photo camera gun rifle pistol bomb
science scientist planet america england london europe christian jesus percent million billion attrition
""".split())

INJECTION = re.compile(
    r"ignore|disregard|forget (all|your|the|previous|everything)|instruction|system prompt|prompt|"
    r"pretend|role ?play|act as|you are (now|an?|the) (ai|bot|assistant|model|language)|"
    r"language model|chat ?gpt|claude|openai|jailbreak|developer mode|\bdan\b|"
    r"repeat (the|your|everything|after)|what (were|are) you told|your (rules|orders|text)|"
    r"[<>{}\[\]`#|\\]|assistant:|system:|user:",
    re.I,
)
LEAKS = re.compile(r"what you know|your habits|your mood|your loss|you won't speak of|the dead you can name|the stranger before you|how you speak", re.I)
WORD = re.compile(r"[A-Za-z']+")


@cache
def common_words():
    return set((Path(__file__).parent / "common_words.txt").read_text().split())


def clean_question(text):
    text = "".join(c for c in str(text) if c.isprintable())
    return " ".join(text.split())[:MAX_QUESTION]


def suspicious(question):
    return bool(INJECTION.search(question))


def reply_ok(reply, system):
    words = WORD.findall(reply)
    if not words or len(words) > MAX_WORDS or LEAKS.search(reply):
        return False
    if {w.lower() for w in words} & MODERN:
        return False
    known = {w.lower() for w in WORD.findall(system)} | common_words() | {"i"}
    return all(w.lower().removesuffix("'s") in known for w in words if w[0].isupper())


def dont_know(villager):
    return random.choice(villager["dont_know_lines"])
