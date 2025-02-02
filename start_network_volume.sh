#!/usr/bin/env bash

# Set default model if its not set in the environment variable
if [ -z "${MODEL+x}" ]; then
  MODEL="cloudyu/Mixtral_34Bx2_MoE_60B"
fi

# Replace slashes with underscores
MODEL="${MODEL//\//_}"
echo "Model: ${MODEL}"

if [[ ! -L /workspace ]]; then
  echo "Symlinking files from Network Volume"
  ln -s /runpod-volume /workspace
fi

if [ -d "/runpod-volume/text-generation-webui/models/${MODEL}" ]; then
  echo "Starting Oobabooga Text Generation Server"
  cd /runpod-volume/text-generation-webui
  source /workspace/venv/bin/activate
  mkdir -p /runpod-volume/logs
  nohup python3 server.py \
    --listen \
    --api \
    --model ${MODEL} \
    --loader ExLlamav2_HF \
    --trust-remote-code \
    --listen-port 3000 \
    --api-blocking-port 5000 \
    --api-streaming-port 5005 &> /runpod-volume/logs/textgen.log &

  echo "Starting RunPod Handler"
  export PYTHONUNBUFFERED=1
  python3 -u /rp_handler.py
else
  echo "Model directory not found!"
fi
