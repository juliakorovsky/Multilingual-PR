import os
import random
from dataclasses import dataclass
from os import path as osp
from typing import Any, ClassVar, Dict, List, Optional

import pytorch_lightning as pl
import simple_parsing
import torch
import torch.optim

################################## Global parameters ##################################

@dataclass
class Hparams:
    """Hyperparameters of for the run"""

    wandb_entity    : str          = "asr-project"         # name of the project
    debug           : bool         = False            # test code before running, if testing, no checkpoints are written
    wandb_project   : str          = "test-asr"
    root_dir        : str          = os.getcwd()  # root_dir
    seed_everything : Optional[int]= None   # seed for the whole run
    tune_lr         : bool         = False  # tune the model on first run
    gpu             : int          = 0      # number or gpu
    max_epochs      : int          = 30    # maximum number of epochs
    weights_path    : str          = "weights"
    dev_run         : bool         = True
    train           : bool         = True
    best_model      : str          = "" # then galant
    compute_features    : int      = True

@dataclass
class NetworkParams:
    network_name       : Optional[str] = "MLP"     # dataset, use <Dataset>Eval for FT
    weight_checkpoint  : str           = ""
    artifact           : str           = ""
    dropout            : float         = 0.75
    normalization      : str           = 'BatchNorm1d'
    activation         : str           = 'GELU'
    input_size         : int           = 1000

@dataclass
class FeatExtractParams:
    network_name                  : str           = "Wav2vec"     # HuBERT, Wav2vec, WavLM
    path_features                 : str           = osp.join(os.getcwd(), "assets")    # HuBERT, Wav2vec
    feature_size                  : int           = 1
    sampling_rate                 : int           = 16000
    padding_value                 : float         = 0.0
    do_normalize                  : bool          = True
    return_attention_mask         : bool          = True 
    split                         : str           = "validation"

@dataclass
class OptimizerParams: 
    """Optimization parameters"""

    optimizer     : str   = "Adam"  # Optimizer default vit: AdamW, default resnet50: Adam
    lr            : float = 0.003     # learning rate,               default = 5e-4
    min_lr        : float = 5e-9     # min lr reached at the end of the cosine schedule
    weight_decay  : float = 1e-8

    # Scheduler parameters
    scheduler     : bool  = False
    warmup_epochs : int   = 5
    max_epochs    : int   = 20

@dataclass
class DatasetParams:
    """Dataset Parameters
    ! The batch_size and number of crops should be defined here
    """
    # Hugging Face datasets parameters
    dataset_name            : str                     = "common_voice"    # https://huggingface.co/mozilla-foundation or https://huggingface.co/datasets/common_voice # dataset, use <Dataset>Eval for FT
    use_auth_token          : bool                    = False             # True if use mozilla-foundation datasets
    subset                  : str                     = "br"              # chosen language 
    download_mode           : str                     = "reuse_dataset_if_exists"
    cache_dir               : str                     = osp.join(os.getcwd(), "assets")
    
    # Dataloader parameters
    num_workers             : int                     = 8         # number of workers for dataloadersint
    batch_size              : int                     = 1 

@dataclass
class Parameters:
    """base options."""
    hparams       : Hparams         = Hparams()
    data_param    : DatasetParams   = DatasetParams()
    network_param : NetworkParams   = NetworkParams()
    optim_param   : OptimizerParams = OptimizerParams()
    feat_param    : FeatExtractParams = FeatExtractParams()
    
    def __post_init__(self):
        """Post-initialization code"""
        if self.hparams.seed_everything is None:
            self.hparams.seed_everything = random.randint(1, 10000)
            
        random.seed(self.hparams.seed_everything)
        torch.manual_seed(self.hparams.seed_everything)
        pl.seed_everything(self.hparams.seed_everything)

    @classmethod
    def parse(cls):
        parser = simple_parsing.ArgumentParser()
        parser.add_arguments(cls, dest="parameters")
        args = parser.parse_args()
        instance: Parameters = args.parameters
        return instance