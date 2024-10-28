# Ollama local setup

Using local Ollama with installer in linux (as system service).
You will need a compatible GPU hardware to make it run reasonably fast.

## Install

- Go to the [Ollama](https://ollama.com/download) web site and use the curl + sh installer
- Ensure service is working: `sudo service ollama status`
- See logs: `sudo journalctl -u ollama -f`
- Checkout is using GPU (not CPU)

## Pull models, depending on your hardware (GPU, CPU, HDD)

In my case I've tested local Ollama with the following (old) hardware in an Ubuntu 22.04.5 LTS:

- Intel® Core™ i7-6700HQ CPU @ 2.60GHz × 8
- NVIDIA GeForce GTX 960M (2MB)

Before installing check you have enough space in your HDD.  [Ollama3.1:8b](https://ollama.com/library/llama3.1) weights 4.7GB.

**If you don't have enough space or want to store models in another disk partition see below: [Change Ollama models store folder](#change-ollama-models-store-folder)**

```bash
#recommended
# THIS MODEL DON'T ALLOW CONTEXT SHIFT, SO IT FAILS WHEN CONTEXT IS GETTING BIGGER AND DON'T FIT INTO YOUR VRAM (f.ex making several questions)
ollama pull deepseek-coder-v2:16b
ollama pull codestral
ollama pull codellama
ollama pull llama3.1:8b
```

NOTE: we don't need to `ollama run <model>`, ollama will run the model (if present) when requested by the api.

## Troubleshooting

[Ollama docs/troubleshooting](https://github.com/ollama/ollama/blob/main/docs/troubleshooting.md)

### Change Ollama models store folder

Change ollama models folder to avoid system partition saturation.
[Models](https://ollama.com/library?sort=popular) are big, so I've changed the location folder for Ollama models:

#### Create new folder (and move models)

```bash
data_folder=/mnt/sda5/ollama \
&& sudo mkdir -p "${data_folder}"/models \
&& sudo chown -R ollama:ollama "${data_folder}"
```

If you already have downloaded models, move de folder to the new location

```bash
mv /usr/share/ollama/.ollama/models/ /mnt/sda5/ollama # FOR EXAMPLE, CHANGE PATH HERE!!!
```

#### Set the OLLAMA_MODELS env variable

Edit ollama.service configuration:

```bash
sudo systemctl edit ollama
# add this lines  (SET YOUR PATH)
[Service]
Environment="OLLAMA_MODELS=/mnt/sda5/ollama/models" # FOR EXAMPLE, CHANGE PATH HERE!!!
#Optionally add this line to get debug info:
Environment="OLLAMA_DEBUG=true"
# Environment="OLLAMA_CONTEXT_LEN=2048"
# Environment="OLLAMA_NUM_PREDICT=64"

#save and exit
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### Ollama don't run with CPU in Linux systems after sleep->wake up

A [bash script](scripts/nvidia-linux-restart.sh) is available for automatic start/stop ollama service, nvidia-settings & nvidia driver.

```bash
sudo systemctl stop ollama
sudo rmmod nvidia_uvm && sudo modprobe nvidia_uvm
sudo systemctl start ollama
```
