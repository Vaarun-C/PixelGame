#!/bin/sh
# Local alternative to train_modal.py: LoRA-tune on Apple silicon (needs the Mac on power), then fuse into dialogue/model.
set -e
cd "$(dirname "$0")/.."
BASE=Qwen/Qwen2.5-0.5B-Instruct
.venv/bin/python dialogue/build.py
.venv/bin/python -m mlx_lm lora --model $BASE --train --data dialogue/data/mix --mask-prompt \
  --num-layers 24 --batch-size 4 --grad-accumulation-steps 4 --grad-checkpoint --iters "${ITERS:-1500}" --learning-rate 2e-5 \
  --max-seq-length 1536 --steps-per-eval 1000 --val-batches 20 --adapter-path dialogue/adapters
.venv/bin/python -m mlx_lm fuse --model $BASE --adapter-path dialogue/adapters --save-path dialogue/model
