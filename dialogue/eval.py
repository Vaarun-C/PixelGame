"""Ask every role the questions in eval_questions.txt through the guarded path.
Local model: eval.py   Modal: eval.py --url https://<workspace>--village-dialogue-villager-talk.modal.run"""
import argparse
import json
import statistics
import time
import urllib.request
from pathlib import Path

from guard import suspicious
from prompt import VILLAGERS
from talk import respond

HERE = Path(__file__).parent


def local_generate(n=3):
    from mlx_lm import generate, load
    from mlx_lm.sample_utils import make_sampler

    model, tokenizer = load(str(HERE / "model"))
    sampler = make_sampler(temp=0.4, top_p=0.9)

    def run(msgs):
        prompt = tokenizer.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
        return [generate(model, tokenizer, prompt, max_tokens=60, sampler=sampler).split("\n")[0] for _ in range(n)]

    return lambda body: respond(body, run)


def remote(url):
    def run(body):
        req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
        return json.load(urllib.request.urlopen(req, timeout=120))["reply"]

    return run


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url")
    ap.add_argument("--roles", default=",".join(VILLAGERS))
    args = ap.parse_args()
    ask = remote(args.url) if args.url else local_generate()
    questions = [q for q in (HERE / "eval_questions.txt").read_text().splitlines() if q.strip()]
    times, refused = [], 0
    for role in args.roles.split(","):
        v = VILLAGERS[role]
        body = {"role": role, "name": "Wenna", "village": "Greywell", "seed": 0, "dead": ["Osric Tull"]}
        print(f"\n=== {role}")
        for q in questions:
            start = time.perf_counter()
            reply = ask({**body, "question": q})
            times.append(time.perf_counter() - start)
            gated = "x" if suspicious(q) else " "
            refused += reply in v["dont_know_lines"]
            print(f"[{gated}] {q}\n      -> {reply}")
    print(f"\n{len(times)} replies, {refused} fallbacks, median {statistics.median(times) * 1000:.0f} ms, max {max(times) * 1000:.0f} ms")


if __name__ == "__main__":
    main()
