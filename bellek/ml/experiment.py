# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/ml.experiment.ipynb.

# %% auto 0
__all__ = ['context_wandb']

# %% ../../nbs/ml.experiment.ipynb 3
def context_wandb(entity, project, **kwargs):
    import wandb
    try:
        wandb_run = wandb.init(
            entity=entity,
            project=project,
            **kwargs
        )
        yield wandb_run
    finally:
        if wandb_run:
            wandb.finish()