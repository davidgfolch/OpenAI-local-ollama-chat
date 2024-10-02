# Local IA chat

[![Backend unit tests](https://github.com/davidgfolch/OpenAI-local-ollama-chat/actions/workflows/backend-tests.yml/badge.svg)](https://github.com/davidgfolch/OpenAI-local-ollama-chat/actions/workflows/backend-tests.yml)

This project implements a chat with the following tech-stack:

Vue -> Python (langchain/openai) -> Ollama

## Ollama (local setup)

Using local Ollama with installer in linux (as system service).
You will need a compatible GPU hardware to make it run reasonably fast.

### Install

- Go to the [Ollama](https://ollama.com/download) web site and use the curl + sh installer
- Ensure service is working: `sudo service ollama status`
- See logs: `sudo journalctl -u ollama -f`
- Checkout is using GPU (not CPU)

### Pull models, depending on your hardware (GPU, CPU, HDD)

In my case I've tested local Ollama with the following hardware:

- Intel® Core™ i7-6700HQ CPU @ 2.60GHz × 8
- NVIDIA GeForce GTX 960M (2MB)
- Ubuntu 22.04.5 LTS

Before installing check you have enough space in your HDD.  [Ollama3.1:8b](https://ollama.com/library/llama3.1) weights 4.7GB.

**If you don't have enough space or want to store models in another disk partition see below: [Change Ollama models store folder](#change-ollama-models-store-folder)**

```bash
  #recomended for code generation you'll need 32GB minimum memory
  ollama pull codestral
  #recommended
  ollama pull llama3.1:8b
```

NOTE: we don't need to `ollama run <model>`, ollama will run the model (if present) when requested by the api.

### Troubleshooting

[Ollama docs/troubleshooting](https://github.com/ollama/ollama/blob/main/docs/troubleshooting.md)

#### Change Ollama models store folder

Change ollama models folder to avoid system partition saturation.
[Models](https://ollama.com/library?sort=popular) are big, so I've changed the location folder for Ollama models:

##### Create new folder (and move models)

```bash
data_folder=/mnt/sda5/ollama \
&& sudo mkdir -p "${data_folder}"/models \
&& sudo chown -R ollama:ollama "${data_folder}"
```

If you already have downloaded models, move de folder to the new location

```bash
mv /usr/share/ollama/.ollama/models/ /mnt/sda5/ollama
```

##### Set the OLLAMA_MODELS env variable

> - Didn't work sudo systemctl edit ollama so edited ollama.service directly
> - Didn't work export OLLAMA_MODELS in ~/.zshrc did not work when restarting ollama
Change ollama.service

```bash
sudo nano /etc/systemd/system/ollama.service
# add this line at the end of [Service] block
Environment="OLLAMA_MODELS=/mnt/sda5/ollama/models"
#save and exit
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

#### Ollama don't run with CPU after Linux systems sleep->wake up

```bash
sudo systemctl stop ollama
sudo rmmod nvidia_uvm && sudo modprobe nvidia_uvm
sudo systemctl start ollama
```

## Project run

### Run Ollama and load model

```bash
sudo service ollama start
ollama run llama3.1:8b # this will take a while the first time
```

### Run backend & frontend

See respective README.md docs: [backend](backend/README.md) & [frontend](frontend/README.md)
