# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/qa.jerxrm.ipynb.

# %% auto 0
__all__ = ['log', 'DEFAULT_MODEL', 'USER_PROMPT', 'SYSTEM_PROMPT', 'SYSTEM_PROMPT_REASONING', 'SYSTEM_PROMPT_WITH_TRIPLETS',
           'SYSTEM_PROMPT_REASONING_WITH_TRIPLETS', 'QuestionAnsweringResult', 'answer_question',
           'QuestionAnsweringResultWithReasoning', 'answer_question_with_reasoning',
           'QuestionAnsweringResultWithTriplets', 'answer_question_with_triplets',
           'QuestionAnsweringResultReasoningWithTriplets', 'answer_question_reasoning_with_triplets']

# %% ../../nbs/qa.jerxrm.ipynb 4
import magentic
from pydantic import BaseModel, Field

from ..logging import get_logger

log = get_logger(__name__)

# %% ../../nbs/qa.jerxrm.ipynb 5
DEFAULT_MODEL = magentic.OpenaiChatModel("gpt-3.5-turbo", temperature=0.1)

# %% ../../nbs/qa.jerxrm.ipynb 6
USER_PROMPT = """The context information is provided below.
---------------------
{context}
---------------------
Given the context information and not prior knowledge, answer the question.
{question}
"""

# %% ../../nbs/qa.jerxrm.ipynb 7
SYSTEM_PROMPT = """You are an excellent question-answering system known for providing accurate and reliable answers. Your responses should be solely based on the context information given, without drawing on prior knowledge."""

class QuestionAnsweringResult(BaseModel):
    """Data model for answering the question."""

    answer: str = Field(description="The answer to the question in 2-4 words.")


@magentic.chatprompt(
    magentic.SystemMessage(SYSTEM_PROMPT), 
    magentic.UserMessage(USER_PROMPT),
    model=DEFAULT_MODEL,
)
def answer_question(
    context: str,
    question: str,
) -> QuestionAnsweringResult: ...

# %% ../../nbs/qa.jerxrm.ipynb 8
SYSTEM_PROMPT_REASONING = """You are an excellent question-answering system known for providing accurate and reliable answers. Your responses should be solely based on the context information given, without drawing on prior knowledge. Always provide clear and logical step-by-step reasoning in your answers."""

class QuestionAnsweringResultWithReasoning(BaseModel):
    """Data model for answering the question."""

    reasoning: str = Field(description="Step-by-step reasoning for the answer.")
    answer: str = Field(description="The answer to the question in 2-4 words.")


@magentic.chatprompt(
    magentic.SystemMessage(SYSTEM_PROMPT_REASONING), 
    magentic.UserMessage(USER_PROMPT),
    model=DEFAULT_MODEL,
)
def answer_question_with_reasoning(
    context: str,
    question: str,
) -> QuestionAnsweringResultWithReasoning: ...

# %% ../../nbs/qa.jerxrm.ipynb 9
SYSTEM_PROMPT_WITH_TRIPLETS = """You are an excellent question-answering system known for providing accurate and reliable answers. Your responses should be solely based on the context information given, without drawing on prior knowledge.

Before answering the question, first, you extract relevant entity-relation-entity triplets from the context. Then, you answer the question based on the triplets. For instance, 

# Example
Context: "Glenhis Hernández (born 7 October 1990 in Havana) is a taekwondo practitioner from Cuba. She was the 2013 World
Champion in middleweight.

The current mayor of Havana ("President of the People's Power Provincial Assembly") is Marta Hernández Romero, she
was elected on March 5, 2011."

Question: "Who is the current mayor of city Glenhis Hernández?"

Triplets: "Glenhis Hernández (Athlete) | born on | October 7, 1990
Glenhis Hernández (Athlete) | birth place | Havana
Glenhis Hernández (Athlete) | specializes in | taekwondo
Glenhis Hernández (Athlete) | won | 2013 World Champion title (Middleweight)
Marta Hernández Romero (Politician) | serves as | mayor of Havana
Marta Hernández Romero (Politician) | holds | the position of "President of the People's Power Provincial Assembly"
Marta Hernández Romero (Politician) | elected on | March 5, 2011."

Answer: "Marta Hernández Romero"
"""

class _QuestionAnsweringResultWithTriplets(BaseModel):
    """Data model for answering the question."""

    triplets: list[str] = Field(description="A list of entity-relation-entity triplets extracted from the context.")
    answer: str = Field(description="The answer to the question in 2-4 words.")

class QuestionAnsweringResultWithTriplets(_QuestionAnsweringResultWithTriplets):
    reasoning: str = ""

@magentic.chatprompt(
    magentic.SystemMessage(SYSTEM_PROMPT_WITH_TRIPLETS), 
    magentic.UserMessage(USER_PROMPT),
    model=DEFAULT_MODEL,
)
def _answer_question_with_triplets(
    context: str,
    question: str,
) -> _QuestionAnsweringResultWithTriplets: ...

def answer_question_with_triplets(
    context: str,
    question: str,
) -> QuestionAnsweringResultWithTriplets: 
    result = _answer_question_with_triplets(context, question)
    return QuestionAnsweringResultWithTriplets(triplets=result.triplets, answer=result.answer)

# %% ../../nbs/qa.jerxrm.ipynb 10
SYSTEM_PROMPT_REASONING_WITH_TRIPLETS = """You are an excellent question-answering system known for providing accurate and reliable answers. Your responses should be solely based on context the information given, without drawing on prior knowledge. Always provide clear and logical step-by-step reasoning in your answers.

Before answering the question, first, you extract relevant entity-relation-entity triplets from the context. Then, you answer the question based on the triplets. For instance, 

# Example
Context: "Glenhis Hernández (born 7 October 1990 in Havana) is a taekwondo practitioner from Cuba. She was the 2013 World
Champion in middleweight.

The current mayor of Havana ("President of the People's Power Provincial Assembly") is Marta Hernández Romero, she
was elected on March 5, 2011."

Question: "Who is the current mayor of city Glenhis Hernández?"

Triplets: "Glenhis Hernández (Athlete) | born on | October 7, 1990
Glenhis Hernández (Athlete) | birth place | Havana
Glenhis Hernández (Athlete) | specializes in | taekwondo
Glenhis Hernández (Athlete) | won | 2013 World Champion title (Middleweight)
Marta Hernández Romero (Politician) | serves as | mayor of Havana
Marta Hernández Romero (Politician) | holds | the position of "President of the People's Power Provincial Assembly"
Marta Hernández Romero (Politician) | elected on | March 5, 2011."

Reasoning: Glenhis Hernández (Athlete) | birth place | Havana
This indicates that Glenhis Hernández was born in Havana.

Marta Hernández Romero (Politician) | serves as | mayor of Havana
This states that Marta Hernández Romero is the mayor of Havana.

From these triplets, we conclude that Marta Hernández Romero is the mayor of Havana.

Answer: "Marta Hernández Romero"
"""

class QuestionAnsweringResultReasoningWithTriplets(BaseModel):
    """Data model for answering the question."""

    triplets: list[str] = Field(description="A list of entity-relation-entity triplets extracted from the context.")
    reasoning: str = Field(description="Step-by-step reasoning for the answer.")
    answer: str = Field(description="The answer to the question in 2-4 words.")


@magentic.chatprompt(
    magentic.SystemMessage(SYSTEM_PROMPT_REASONING_WITH_TRIPLETS), 
    magentic.UserMessage(USER_PROMPT),
    model=DEFAULT_MODEL,
)
def answer_question_reasoning_with_triplets(
    context: str,
    question: str,
) -> QuestionAnsweringResultReasoningWithTriplets: ...