# backend

## Project setup

### Prerequisites

[Install](https://docs.anaconda.com/miniconda/#quick-command-line-install) Conda. 

> See also: [Conda getting started](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html#before-you-start)

```bash
source ~/miniconda3/bin/activate
conda init zsh
eval "$(/home/slks/miniconda3/bin/conda shell.zsh hook)"
```

### Install dependencies

[Activate environment](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html#installing-packages) to install dependencies:

```bash
conda activate ./.venv
```

NOTE: if dependencies added should be exported to `env.yml`:
  
```bash
conda env export > env.yml 
```

## Run the backend

```bash
cd backend 
python api.py
```

Default host/port is set in [host.py](host.py).

You'll see logs of operations (see [logConfig.py](logConfig.py)).

Flask api found in [api.py](api.py), this is also the main entry point.

OpenAi/langchain implementation in [iaServer.py](iaServer.py).
