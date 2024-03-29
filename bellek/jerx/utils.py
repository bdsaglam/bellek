# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/jerx.utils.ipynb.

# %% auto 0
__all__ = ['log', 'Entity', 'Relation', 'Triplet', 'parse_triplet_strings', 'parse_triplets']

# %% ../../nbs/jerx.utils.ipynb 3
from typing import TypeAlias, Iterable, Callable, Any, Generator

from ..logging import get_logger

log = get_logger(__name__)

# %% ../../nbs/jerx.utils.ipynb 4
Entity: TypeAlias = str|tuple[str, str]
Relation: TypeAlias = str
Triplet: TypeAlias = tuple[Entity, Relation, Entity]

# %% ../../nbs/jerx.utils.ipynb 5
def parse_triplet_strings(text: str, delimiter: str="|") -> list[str]:
    return [line for line in text.splitlines() if line and line.count(delimiter) == 2]

def parse_triplets(text: str, delimiter: str="|") -> list[Triplet]:
    return [tuple([s.strip() for s in triplet_string.split(delimiter)]) for triplet_string in parse_triplet_strings(text, delimiter=delimiter)]
