# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/ml.wandb.ipynb.

# %% auto 0
__all__ = ['log', 'fetch_wandb_run', 'fetch_wandb_config']

# %% ../../nbs/ml.wandb.ipynb 3
import wandb
from ..logging import get_logger

log = get_logger(__name__)

# %% ../../nbs/ml.wandb.ipynb 4
def fetch_wandb_run(*, entity: str, project: str, run_id: str):
    return wandb.Api().run(f"{entity}/{project}/{run_id}")

def fetch_wandb_config(*, entity: str, project: str, run_id: str):
    run = fetch_wandb_run(entity=entity, project=project, run_id=run_id)
    return run.config