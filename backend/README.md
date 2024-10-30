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
conda env update --file backend/env.yml --name langchain --prune
```

NOTE: if dependencies added should be exported to `env.yml`:
  
```bash
conda env export > backend/env.yml --no-builds
```

Other [Conda](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html) commands:

```bash
conda create langchain
conda deactivate # deactivate any active conda environment
conda activate langchain
conda env create -f backend/env.yml

#todo: try setting python version
conda create -n tf_env python=3.8 
```

## Run the backend

```bash
cd backend && python api.py
```

## Tests & coverage

```bash
cd backend
# run tests
python -m pytest 
# run coverage
coverage run --source=src -m pytest 
coverage report -m
# see coverage
coverage html
```

All in one:

```bash
pytest && coverage run --source=src -m pytest && coverage report -m
```

## Generate coverage badge for README.md

```bash
cd backend
coverage-badge -o ../README.md_images/coverage.svg -f
```

NOTE: pipeline generation don't work

## Project details

Default host/port is set in [host.py](src/service/host.py).

You'll see operations' logs in console (see [logUtil.py](src/util/logUtil.py)).

Flask api is implemented in [api.py](src/api/api.py), this is also the main entry point.

OpenAi/langchain implementation in [iaService.py](src/service/aiService.py).

## Reference

- [Flask](https://flask.palletsprojects.com/en/2.3.x/)
- [Flask streaming](https://flask.palletsprojects.com/es/main/patterns/streaming/)
- [Coverage](https://coverage.readthedocs.io/en/7.6.1/)