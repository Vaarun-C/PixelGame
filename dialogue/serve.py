"""Villager dialogue on Modal. Deploy: .venv/bin/modal deploy dialogue/serve.py (after train_modal.py fills the volume)."""
from pathlib import Path

import modal

HERE = Path(__file__).parent
CODE = ["guard.py", "prompt.py", "talk.py", "villagers.json", "common_words.txt"]
CANDIDATES = 3

image = (
    modal.Image.from_registry("vllm/vllm-openai:v0.15.1", setup_dockerfile_commands=["RUN ln -sf $(which python3) /usr/bin/python"])
    .entrypoint([])
    .pip_install("fastapi[standard]")
    .env({"VLLM_SERVER_DEV_MODE": "1", "TORCH_CPP_LOG_LEVEL": "FATAL"})
)
volume = modal.Volume.from_name("village-dialogue")
for name in CODE:
    image = image.add_local_file(HERE / name, f"/root/{name}")

app = modal.App("village-dialogue")


@app.cls(
    image=image,
    gpu=["L4", "A10G"],
    scaledown_window=5 * 60,
    max_containers=1,
    volumes={"/out": volume},
    enable_memory_snapshot=True,
    experimental_options={"enable_gpu_snapshot": True},
)
class Villager:
    @modal.enter(snap=True)
    def load(self):
        from vllm import LLM, SamplingParams

        from guard import MODERN

        self.llm = LLM("/out/model", max_model_len=2048, gpu_memory_utilization=0.5, enable_prefix_caching=True, enable_sleep_mode=True)
        self.params = SamplingParams(n=CANDIDATES, temperature=0.4, top_p=0.9, max_tokens=60, stop=["\n"], bad_words=sorted(MODERN))
        self.generate([{"role": "user", "content": "Who are you?"}])
        self.llm.sleep(level=1)

    @modal.enter(snap=False)
    def wake(self):
        self.llm.wake_up()

    def generate(self, msgs):
        return [o.text for o in self.llm.chat([msgs], self.params, use_tqdm=False)[0].outputs]

    @modal.fastapi_endpoint(method="POST")
    def talk(self, body: dict):
        from talk import respond

        return {"reply": respond(body, self.generate)}
