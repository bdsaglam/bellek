# AUTOGENERATED! DO NOT EDIT! File to edit: ../../../nbs/llama_index.data_structs.data_structs.ipynb.

# %% auto 0
__all__ = ['KG', 'patch_kg_data_struct']

# %% ../../../nbs/llama_index.data_structs.data_structs.ipynb 3
from dataclasses import dataclass, field
from typing import Dict, List, Set

from llama_index.data_structs.struct_type import IndexStructType
from llama_index.data_structs.data_structs import IndexStruct
from ...text.utils import fuzzy_match
from llama_index.schema import BaseNode

# %% ../../../nbs/llama_index.data_structs.data_structs.ipynb 4
@dataclass
class KG(IndexStruct):
    """A table of keywords mapping keywords to text chunks."""

    # Unidirectional

    # table of keywords to node ids
    table: Dict[str, Set[str]] = field(default_factory=dict)

    # TODO: legacy attribute, remove in future releases
    rel_map: Dict[str, List[List[str]]] = field(default_factory=dict)

    # TBD, should support vector store, now we just persist the embedding memory
    # maybe chainable abstractions for *_stores could be designed
    embedding_dict: Dict[str, List[float]] = field(default_factory=dict)

    # keyword match params
    keyword_match_threshold: float = 0.6

    @property
    def node_ids(self) -> Set[str]:
        """Get all node ids."""
        return set.union(*self.table.values())

    def add_to_embedding_dict(self, triplet_str: str, embedding: List[float]) -> None:
        """Add embedding to dict."""
        self.embedding_dict[triplet_str] = embedding

    def add_node(self, keywords: List[str], node: BaseNode) -> None:
        """Add text to table."""
        node_id = node.node_id
        for keyword in keywords:
            if keyword not in self.table:
                self.table[keyword] = set()
            self.table[keyword].add(node_id)

    def search_node_by_keyword(self, keyword: str) -> Dict[str, List[str]]:
        result = dict()
        for k, node_set in self.table.items():
            if fuzzy_match(keyword, k, threshold=self.keyword_match_threshold):
                result[k] = list(node_set)
        return result
    
    @classmethod
    def get_type(cls) -> IndexStructType:
        """Get type."""
        return IndexStructType.KG


# %% ../../../nbs/llama_index.data_structs.data_structs.ipynb 5
def patch_kg_data_struct():
    from llama_index.data_structs.registry import INDEX_STRUCT_TYPE_TO_INDEX_STRUCT_CLASS
     
    INDEX_STRUCT_TYPE_TO_INDEX_STRUCT_CLASS[IndexStructType.KG] =  KG
