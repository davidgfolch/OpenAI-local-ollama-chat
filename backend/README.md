# Backend

## Project setup

### Prerequisite: Install Conda

Follow the conda documentation: [Installing Conda](https://docs.anaconda.com/miniconda/#quick-command-line-install). See also [Conda getting started](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html#before-you-start)

Setup your terminal (zsh example):
```bash
source ~/miniconda3/bin/activate
conda init zsh
eval "$(/home/slks/miniconda3/bin/conda shell.zsh hook)"
```

### Install dependencies

```bash
conda env update --file env.yml --name base --prune
```

NOTE: if dependencies added should be exported to `env.yml`:
  
```bash
conda env export > env.yml --from-history
```

Other [Conda](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html) commands:

```bash
conda create langchain
conda deactivate # deactivate any active conda environment
conda activate langchain
conda env create -f env.yml
```

## Run the backend

```bash
cd backend 
python api.py
```

## Project details

Default host/port is set in [host.py](host.py).

You'll see operations' logs in console (see [logConfig.py](logConfig.py)).

Flask api is implemented in [api.py](api.py), this is also the main entry point.

OpenAi/langchain implementation in [iaServer.py](iaServer.py).
