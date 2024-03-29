# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/jerx.eval.ipynb.

# %% auto 0
__all__ = ['log', 'evaluate_jerx_single', 'evaluate_jerx', 'evaluate_pipe_jerx', 'evaluate_model_jerx']

# %% ../../nbs/jerx.eval.ipynb 3
from operator import eq
from typing import Iterable, Callable, Any, Generator
import numpy as np
from .utils import Triplet, parse_triplet_strings
from ..utils import is_in
from ..logging import get_logger

log = get_logger(__name__)

# %% ../../nbs/jerx.eval.ipynb 4
def evaluate_jerx_single(*, reference: Iterable[Triplet], prediction: Iterable[Triplet], eq_fn=eq):
    """
    Example: [(('John', 'PERSON'), 'works_at', ('Google', 'ORG'))]
    """

    reference_set = set(reference)
    prediction_set = set(prediction)
    if len(reference) != len(reference_set):
        log.warning("Duplicates found in references.")

    tp = sum(int(is_in(item, prediction, eq_fn=eq_fn)) for item in reference)
    fp = len(prediction_set) - tp
    fn = len(reference_set) - tp
    
    # Calculate metrics
    precision = tp / (tp + fp) if tp + fp > 0 else 0
    recall = tp / (tp + fn) if tp + fn > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if precision + recall > 0 else 0
    
    return {
        'precision': precision,
        'recall': recall,
        'f1': f1_score
    }

def evaluate_jerx(*, references: Iterable[Iterable[Triplet]], predictions: Iterable[Iterable[Triplet]]):
    score_dicts = [
        evaluate_jerx_single(reference=reference, prediction=prediction) 
        for reference, prediction in zip(references, predictions)
    ]
    return {('mean_' + key): np.mean([scores[key] for scores in score_dicts]) for key in score_dicts[0].keys()}

# %% ../../nbs/jerx.eval.ipynb 8
def evaluate_pipe_jerx(dataset, pipe):
    import evaluate

    log.info(f"Evaluating model for JER on dataset with {len(dataset)} samples.")

    tokenizer = pipe.tokenizer

    def _clean(text):
        return text.replace(tokenizer.special_tokens_map["eos_token"], "").strip()

    results = pipe(dataset["input"])
    generations = [result[0]["generated_text"] for result in results]
    predictions = [parse_triplet_strings(_clean(text)) for text in generations]
    references = [parse_triplet_strings(_clean(text)) for text in dataset["output"]]

    dataf = dataset.to_pandas()
    dataf["generation"] = generations
    dataf["prediction"] = predictions
    dataf["reference"] = references

    metric = evaluate.load("bdsaglam/jer")
    scores = metric.compute(predictions=predictions, references=references)

    return scores, dataf


def evaluate_model_jerx(
    dataset,
    *,
    response_template: str,
    tokenizer,
    model,
    max_new_tokens=256,
    batch_size=4,
    **kwargs,
):
    assert len(dataset) > 0, "Dataset is empty!"

    def extract_input_output(example):
        input, output = example["text"].rsplit(response_template, 1)
        input += response_template
        return {"input": input, "output": output}

    dataset = dataset.map(extract_input_output)

    # setup generation pipeline
    from transformers import pipeline

    pipe = pipeline(
        task="text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=max_new_tokens,
        batch_size=batch_size,
        return_full_text=False,
        **kwargs,
    )

    return evaluate_pipe_jerx(dataset, pipe)
