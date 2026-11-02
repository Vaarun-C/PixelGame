"""Fine-tune the base model on data/mix on a Modal GPU; weights land in the village-dialogue volume.
Run: .venv/bin/python dialogue/build.py && .venv/bin/modal run dialogue/train_modal.py"""
from pathlib import Path

import modal

BASE = "Qwen/Qwen2.5-0.5B-Instruct"
HERE = Path(__file__).parent

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("torch==2.8.0", "transformers==4.56.2", "trl==0.23.0", "datasets==4.1.1")
    .add_local_dir(HERE / "data" / "mix", "/data")
)
volume = modal.Volume.from_name("village-dialogue", create_if_missing=True)
app = modal.App("village-dialogue-train")


@app.function(image=image, gpu=["L4", "A10G", "L40S"], timeout=2 * 60 * 60, volumes={"/out": volume})
def train(epochs: float = 2, lr: float = 1e-5):
    from datasets import load_dataset
    from trl import SFTConfig, SFTTrainer

    def split(row):
        return {"prompt": row["messages"][:-1], "completion": row["messages"][-1:]}

    data = load_dataset("json", data_files={"train": "/data/train.jsonl", "valid": "/data/valid.jsonl"}).map(split, remove_columns=["messages"])
    config = SFTConfig(
        output_dir="/tmp/run",
        num_train_epochs=epochs,
        learning_rate=lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        gradient_checkpointing=True,
        max_length=1536,
        bf16=True,
        logging_steps=25,
        eval_strategy="steps",
        eval_steps=200,
        save_strategy="no",
        report_to="none",
    )
    trainer = SFTTrainer(model=BASE, args=config, train_dataset=data["train"], eval_dataset=data["valid"])
    trainer.train()
    print(trainer.evaluate())
    trainer.save_model("/out/model")
    trainer.processing_class.save_pretrained("/out/model")
    volume.commit()
