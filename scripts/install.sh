#!/usr/bin/env bash

COMMIT="2af7e382b121f2eae16dd1f7ace621d31028b319"
TORCH_VERSION="2.2.0"
MODEL="LoneStriker/Air-Striker-Mixtral-8x7B-Instruct-ZLoss-3.75bpw-h6-exl2"

echo "Deleting Oobabooga Text Generation Web UI"
rm -rf /workspace/text-generation-webui

echo "Deleting venv"
rm -rf /workspace/venv

echo "Cloning Oobabooga Text Generation Web UI repo to /workspace"
cd /workspace
git clone https://github.com/oobabooga/text-generation-webui.git
cd text-generation-webui
git checkout ${COMMIT}

echo "Installing Ubuntu updates"
apt update
apt -y upgrade

echo "Creating and activating venv"
cd /workspace/text-generation-webui
python3 -m venv /workspace/venv
source /workspace/venv/bin/activate

echo "Installing Torch 2.2.0"
pip3 install --no-cache-dir torch==${TORCH_VERSION} torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo "Installing xformers"
pip3 install --no-cache-dir xformers

echo "Installing Oobabooga Text Generation Web UI"
pip3 install -r requirements.txt
bash -c 'for req in extensions/*/requirements.txt ; do pip3 install -r "$req" ; done'

echo "Installing repositories"
mkdir -p repositories
cd repositories
git clone https://github.com/turboderp/exllama
pip3 install -r exllama/requirements.txt

pip3 uninstall -y exllamav2
pip3 install exllamav2==0.0.13
pip3 install flash-attn==2.3
pip3 install xformers==0.0.21

echo "Installing RunPod Serverless dependencies"
cd /workspace/text-generation-webui
pip3 install huggingface_hub runpod

echo "Downloading model: ${MODEL}"
cd /workspace/text-generation-webui
python3 download-model.py ${MODEL} \
  --output /workspace/text-generation-webui/models

echo "Creating log directory"
mkdir -p /workspace/logs
