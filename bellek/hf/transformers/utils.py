# AUTOGENERATED! DO NOT EDIT! File to edit: ../../../nbs/hf.transformers.utils.ipynb.

# %% auto 0
__all__ = ['log', 'merge_adapters_and_publish', 'load_tokenizer_model']

# %% ../../../nbs/hf.transformers.utils.ipynb 3
from copy import deepcopy
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from ...utils import NestedDict
from ...logging import get_logger

log = get_logger(__name__)

# %% ../../../nbs/hf.transformers.utils.ipynb 4
def merge_adapters_and_publish(
    model_id: str,
    torch_dtype=torch.float16,
    device_map={"": 0},
    merged_model_id: str=None,
):
    from peft import AutoPeftModelForCausalLM
    
    if isinstance(torch_dtype, str) and torch_dtype != "auto":
        torch_dtype = getattr(torch, torch_dtype) 

    log.info(f"Loading model and tokenizer for {model_id}")
    model = AutoPeftModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch_dtype,
        device_map=device_map,
    )
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)

    log.info("Merging adapters to model...")
    model = model.merge_and_unload()

    if merged_model_id is None:
        merged_model_id = f"{model_id}-merged"
    log.info(f"Pushing merged model to HF hub as {merged_model_id}")
    model.push_to_hub(merged_model_id)
    tokenizer.push_to_hub(merged_model_id)
    return merged_model_id

# %% ../../../nbs/hf.transformers.utils.ipynb 5
def load_tokenizer_model(
    model_name_or_path: str,
    *,
    auto_model_cls=None,
    device_map={"": 0},
    **model_kwargs,
):
    if auto_model_cls is None:
        if "-peft" in model_name_or_path:
            from peft import AutoPeftModelForCausalLM
            auto_model_cls = AutoPeftModelForCausalLM
        else:
            auto_model_cls = AutoModelForCausalLM

    # Setup quantization config
    if (quantization_config := model_kwargs.get("quantization_config")) and isinstance(quantization_config, dict):
        from transformers import BitsAndBytesConfig
        model_kwargs["quantization_config"] = BitsAndBytesConfig(**quantization_config)
    # Setup torch dtype
    if (torch_dtype := model_kwargs.get("torch_dtype")) and (torch_dtype != "auto"):
        model_kwargs["torch_dtype"] = getattr(torch, torch_dtype)
    # Load model
    model = auto_model_cls.from_pretrained(
        model_name_or_path,
        device_map=device_map,
        **model_kwargs,
    )
    # Load tokenizer
    if auto_model_cls == AutoModelForCausalLM:
        tokenizer_id = model_name_or_path
    else:
        from peft import AutoPeftModelForCausalLM
        if auto_model_cls == AutoPeftModelForCausalLM:
            tokenizer_id = model.active_peft_config.base_model_name_or_path
        else:
            raise ValueError(f"Unknown auto_model_cls: {auto_model_cls}")
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_id, trust_remote_code=True)
    return tokenizer, model
