#!/bin/bash

model=bdsaglam/llama-2-7b-chat-hf-kg-cons-merged
# model=NousResearch/Llama-2-7b-chat-hf

VOLUME="${HOME}/.cache/huggingface/tgi"
mkdir -p $VOLUME

# IMAGE=ghcr.io/huggingface/text-generation-inference:latest
IMAGE=bdsaglam/text-generation-inference:latest

docker run --gpus all --shm-size 1g \
    -p 8080:80 \
    -v "${VOLUME}":/data \
    -e HUGGING_FACE_HUB_TOKEN=$HUGGING_FACE_HUB_TOKEN \
    $IMAGE \
    --trust-remote-code --model-id $model --quantize bitsandbytes-nf4 --dtype bfloat16