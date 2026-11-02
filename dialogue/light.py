"""LIGHT (facebookresearch, MIT) -> chat examples for the voice. Usage: light.py <light-dialog-processed-small7.pkl>"""
import collections
import json
import pickle
import re
import sys
from pathlib import Path

from guard import MODERN
from prompt import light_prompt, messages

HERE = Path(__file__).parent
WORD = re.compile(r"[A-Za-z']+")
CHEERFUL = set("happy glad love lovely wonderful great fun delighted excited nice fantastic yay hooray amazing hobby".split())
CREATURES = re.compile(r"\b(fairy|fairies|unicorn|elf|elves|gnome|dragon|troll|goblin|mermaid|pixie|giant|wizard|witch|sprite|ghost|spirit|animal|cat|dog|horse|bird|mouse|rat)s?\b", re.I)


class DataOnly(pickle.Unpickler):
    def find_class(self, module, name):
        raise pickle.UnpicklingError(f"refusing {module}.{name}")


def first_sentences(text, n=2):
    return " ".join(re.split(r"(?<=[.!?])\s+", text.strip())[:n])


def good(line, modern):
    words = [w.lower() for w in WORD.findall(line)]
    return 3 <= len(words) <= 30 and line.count("!") <= 1 and not re.search(r"\d", line) and not set(words) & (modern | CHEERFUL)


def with_article(name):
    return name if name.lower().startswith(("the ", "a ", "an ")) else ("an " if name[0] in "aeiou" else "a ") + name


def examples(episode, modern):
    agents = {a["name"]: a["persona"] for a in episode["agents"]}
    if any(CREATURES.search(name) for name in agents) or any(set(WORD.findall(p.lower())) & CHEERFUL for p in agents.values()):
        return
    setting = episode["setting"]
    speech, speaker = episode["speech"], episode["character"]
    for me in agents:
        system = light_prompt(with_article(me), agents[me], setting["name"], first_sentences(setting["description"]))
        pairs = []
        for i in range(1, len(speech)):
            if speaker[i] != me or speaker[i - 1] == me or not speech[i] or not speech[i - 1]:
                continue
            q, a = " ".join(speech[i - 1].split()), " ".join(speech[i].split())
            if good(q, modern) and good(a, modern):
                yield {"messages": messages(system, pairs[-2:], q) + [{"role": "assistant", "content": a}]}
                pairs.append((q, a))
            else:
                pairs = []


def main(path):
    with open(path, "rb") as f:
        episodes = DataOnly(f).load()
    counts = collections.Counter(w for ep in episodes for line in ep["speech"] if line for w in WORD.findall(line) if w.islower())
    (HERE / "common_words.txt").write_text("\n".join(sorted(w for w, c in counts.items() if c >= 5)) + "\n")

    out = HERE / "data" / "light.jsonl"
    out.parent.mkdir(exist_ok=True)
    n = 0
    with out.open("w") as f:
        for ep in episodes:
            for ex in examples(ep, MODERN):
                f.write(json.dumps(ex) + "\n")
                n += 1
    print(f"{n} examples from {len(episodes)} episodes -> {out}")


if __name__ == "__main__":
    main(sys.argv[1])
