import os
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
from fastai.callback.wandb import *
from fastai.data.all import *
from fastai.torch_core import set_seed
from fastai.vision.all import *
from fastcore.basics import ifnone, store_attr
from torchvision import transforms

from bellek.ml.data import *
from bellek.ml.experiment import *
from bellek.ml.vision import *
from bellek.utils import *


def run_experiment(config, wandb_run):
    print("Config")
    print(wandb_run.config)

    seed = config.get("seed")
    if seed is not None:
        set_seed(seed)

    print("Training...")
    wandb_run.log({"val_loss": 10})


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("--cfg")
    args = parser.parse_args()

    with open(args.cfg) as f:
        config = Tree(json.load(f))

    # prepare config
    if "device" not in config:
        config["device"] = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    for k, v in config.flat().items():
        if isinstance(k, str) and k.endswith("path"):
            config.set(k, str(Path(v).resolve()))

    with context_chdir(make_experiment_dir()):
        wandb_config = config["wandb"]
        with context_wandb(**wandb_config) as wandb_run:
            wandb_run.config.update(config.flat())
            run_experiment(config, wandb_run)