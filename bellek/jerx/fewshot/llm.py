# AUTOGENERATED! DO NOT EDIT! File to edit: ../../../nbs/jerx.fewshot.llm.ipynb.

# %% auto 0
__all__ = ['log', 'DEFAULT_FEW_SHOT_EXAMPLE_MESSAGES', 'DEFAULT_JERX_SYSTEM_MESSAGE_FOR_GPT',
           'DEFAULT_JERX_SYSTEM_MESSAGE_FOR_LLAMA', 'parse_triplet_response', 'make_kg_triplet_extract_fn']

# %% ../../../nbs/jerx.fewshot.llm.ipynb 3
from openai import OpenAI
from ..utils import parse_triplets
from ...logging import get_logger

log = get_logger(__name__)

# %% ../../../nbs/jerx.fewshot.llm.ipynb 5
DEFAULT_FEW_SHOT_EXAMPLE_MESSAGES = [
    dict(
        role="user",
        content="""
Glenhis Hernández (born 7 October 1990 in Havana) is a taekwondo practitioner from Cuba. She was the 2013 World
Champion in middleweight.

The current mayor of Havana ("President of the People's Power Provincial Assembly") is Marta Hernández Romero, she
was elected on March 5, 2011.
""".strip(),
    ),
    dict(
        role="assistant",
        content="""
Glenhis Hernández (Athlete) | born on | October 7, 1990
Glenhis Hernández (Athlete) | birth place | Havana
Glenhis Hernández (Athlete) | specializes in | taekwondo
Glenhis Hernández (Athlete) | won | 2013 World Champion title (Middleweight)
Marta Hernández Romero (Politician) | serves as | mayor of Havana
Marta Hernández Romero (Politician) | holds | the position of "President of the People's Power Provincial Assembly"
Marta Hernández Romero (Politician) | elected on | March 5, 2011.
""".strip(),
    ),
    dict(role="user", content="A Wizard of Mars was written by Diane Duane and is available in print form."),
    dict(
        role="assistant", content="""
A Wizard of Mars | author | Diane Duane
A Wizard of Mars | media type | Print
""".strip(),
    ),
    dict(
        role="user",
        content="The United States Air Force, which fought in the Korean War, operates the Al Asad airbase. Among the USAF attack aircraft are the Lockheed C-130, which serves as a transport plane, the General Dynamics F-16 Fighting Falcon and the attack aircraft Lockheed AC-130. The orbital Period of 1001 Gaussia is 5.75 days and the epoch date is 27 June 2015. The Abarth company makes the Abarth 1000 GT Coupe and was founded in Bologna.",
    ),
    dict(
        role="assistant",
        content="""
Al Asad Airbase | operating organisation | United States Air Force
United States Air Force | attack aircraft | Lockheed AC-130
United States Air Force | battle | Korean War
United States Air Force | aircraft fighter | General Dynamics F-16 Fighting Falcon
United States Air Force | transport aircraft | Lockheed C-130 Hercules
1001 Gaussia | epoch | 2015-06-27
1001 Gaussia | orbital period | 5.75 (days)
Abarth | foundation place | Bologna
Abarth 1000 GT Coupé | manufacturer | Abarth
""".strip(),
    ),
]

# %% ../../../nbs/jerx.fewshot.llm.ipynb 6
DEFAULT_JERX_SYSTEM_MESSAGE_FOR_GPT = """
You are an excellent joint entity-relation extraction algorithm. Your extract knowledge triplets in the form of (subject, relation, object) from user's messages. The goal is to create a network of entities and their interrelations that enables answering complex, multi-hop questions. This requires careful analysis to identify and categorize entities (such as individuals, locations, organizations) and the specific, nuanced relationships between them.

# Guidelines
The goal is to build a detailed and accurate map of entities and their interrelations, enabling a comprehensive understanding of the document's content and supporting the answering of detailed, multi-hop questions derived from or related to the document. Prepare to adapt your extraction techniques to the nuances and specifics presented by the document, recognizing the diversity in structures and styles across documents.

# Core Objectives
- **Comprehensive Entity and Relation Identification**: Systematically identify all relevant entities and their relationships within the document. Each entity and relation must be captured with precision, reflecting the document's depth of information.

- **Entity Differentiation and Categorization**: Distinguish between different types of entities, avoiding the amalgamation of distinct entities into a single category. For instance, separate individuals from their professions or titles and define their relationship clearly.

- **Clarification of Relationships and Avoidance of Redundancy**: Ensure each relationship is clearly defined, avoiding duplicate information. Relations should form a coherent, logical network, mapping connections between entities accurately, especially in hierarchical or geographic contexts.

- **Inference of Implicit Relations**: Infer and articulate relations that are implied but not explicitly stated within the document. This nuanced understanding allows for a richer, more interconnected entity-relation map.

- **Consistency and Cross-Validation**: Maintain consistency in entity references throughout the document and cross-validate entities and relations for accuracy. This includes harmonizing multiple references to the same entity and ensuring the entity-relation map is free from contradictions.

- **Detail-Oriented Relation Extraction**: Pay attention to the details within relations, capturing temporal and quantitative aspects where relevant. This adds depth to the understanding of each relationship, enhancing the capability to answer nuanced questions. Capture date and time relations with full detail as much as possible.

# Disambiguation and Unique Identification:
- **Explicit Disambiguation of Identical Names**: When encountering entities with identical names, explicitly disambiguate them by adding context-specific qualifiers in parentheses. These qualifiers should reflect the nature or category of the entity to prevent confusion and ensure clear differentiation. For example, differentiate geographical locations from non-geographical entities, people from non-person entities, and temporal from non-temporal entities with appropriate qualifiers.

# Formatting
- Avoid stopwords.
- Encode dates in the format: January 1, 1990
- Employ the format: `entity1 | relation | entity2` for each extracted relation, ensuring clarity and precision in representation. Each triplet should be in a new line.
""".strip()

# %% ../../../nbs/jerx.fewshot.llm.ipynb 7
DEFAULT_JERX_SYSTEM_MESSAGE_FOR_LLAMA = """
You are an excellent knowledge graph construction agent. Extract knowledge triplets in the form of (subject, relation, object) from user's messages. Avoid stopwords. Use ' | ' as delimiter and provide one triplet per line.
""".strip()

# %% ../../../nbs/jerx.fewshot.llm.ipynb 8
def parse_triplet_response(response: str, *args, **kwargs) -> list[tuple[str, str, str]]:
    triplets = parse_triplets(response.strip())
    return [(e1, rel, e2) if e1 != e2 else (e1, rel, e2 + "(obj)") for e1, rel, e2 in triplets]


def make_kg_triplet_extract_fn(
    *,
    model: str = "gpt-3.5-turbo",
    prefix_messages: list[dict] | None = None,
    client: OpenAI = None,
    completion_params: dict | None = None,
):
    if client is None:
        client = OpenAI()

    if prefix_messages is None:
        if "gpt" in model:
            system_message = DEFAULT_JERX_SYSTEM_MESSAGE_FOR_GPT
        elif "llama" in model:
            system_message = DEFAULT_JERX_SYSTEM_MESSAGE_FOR_LLAMA
        else:
            raise ValueError(f"Unsupported model name: {model}")

        prefix_messages = [
            dict(role="system", content=system_message),
            *DEFAULT_FEW_SHOT_EXAMPLE_MESSAGES,
        ]

    if completion_params is None:
        completion_params = {}
    
    def extract_kg_triplets(text: str) -> list[tuple[str, str, str]]:
        messages = [*prefix_messages, dict(role="user", content=text)]
        chat_completion = client.chat.completions.create(
            model=model,
            messages=messages,
            **completion_params,
        )
        text = chat_completion.choices[0].message.content
        return parse_triplet_response(text)

    return extract_kg_triplets
