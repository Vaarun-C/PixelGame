"""Mix LIGHT voice examples with lore examples (data/lore/*.jsonl) into data/mix/{train,valid}.jsonl."""
import json
import random
from pathlib import Path

from guard import reply_ok
from prompt import VILLAGERS, messages, villager_prompt

DATA = Path(__file__).parent / "data"
LORE_REPEAT = 2
LIGHT_PER_LORE = 2
VALID_SHARE = 0.05


def lore_example(r):
    v = VILLAGERS[r["role"]]
    system = villager_prompt(r["role"], r["name"], r["village"], r["mood"], r["loss"], r.get("dead", []), r.get("wanderer", ""))
    assert r["mood"] in v["moods"] and r["loss"] in v["losses"], r
    if not reply_ok(r["answer"], system):
        print("dropped:", r["role"], r["answer"])
        return None
    return {"messages": messages(system, r.get("history", []), r["question"]) + [{"role": "assistant", "content": r["answer"]}]}


def read(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main():
    rng = random.Random(7)
    lore = [ex for path in sorted((DATA / "lore").glob("*.jsonl")) for r in read(path) if (ex := lore_example(r))]
    rng.shuffle(lore)
    cut = int(len(lore) * VALID_SHARE)
    light = read(DATA / "light.jsonl")
    rng.shuffle(light)
    light = light[: len(lore) * LIGHT_PER_LORE]

    train = lore[cut:] * LORE_REPEAT + light
    rng.shuffle(train)
    out = DATA / "mix"
    out.mkdir(exist_ok=True)
    for name, rows in (("train", train), ("valid", lore[:cut] + light[:cut])):
        (out / f"{name}.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    print(f"lore {len(lore)}, light {len(light)}, train {len(train)}, valid {2 * cut}")


if __name__ == "__main__":
    main()
