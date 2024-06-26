# AUTOGENERATED! DO NOT EDIT! File to edit: ../../../nbs/jerx.dataset.webnlg.ipynb.

# %% auto 0
__all__ = ['batch_transform_webnlg']

# %% ../../../nbs/jerx.dataset.webnlg.ipynb 3
from ...utils import split_camel_case

# %% ../../../nbs/jerx.dataset.webnlg.ipynb 4
def _transform_relation(relation: str):
    return " ".join([word.lower() for word in split_camel_case(relation)]).strip()


def _transform_entity(entity: str):
    return entity.replace("_", " ").strip()


def _transform_triplet(triplet_string: str):
    delimiter = " | "
    triplet_string = triplet_string.replace('"', "").replace("''", "")
    entity1, relation, entity2 = triplet_string.split(delimiter)
    relation = _transform_relation(relation)
    entity1 = _transform_entity(entity1)
    entity2 = _transform_entity(entity2)
    return delimiter.join([entity1, relation, entity2])


def _batch_transform_webnlg(examples):
    for lex, mts in zip(examples["lex"], examples["modified_triple_sets"]):
        for text in lex["text"]:
            triplets = [_transform_triplet(triplet_string) for triplet_string in mts["mtriple_set"][0]]
            yield dict(text=text, triplets=triplets)


def batch_transform_webnlg(examples):
    records = list(_batch_transform_webnlg(examples))
    return {
        "text": [record["text"] for record in records],
        "triplets": [record["triplets"] for record in records],
    }
