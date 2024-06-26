from datetime import datetime
import json
import shutil
from pathlib import Path

import kuzu
import typer
from dotenv import load_dotenv
from llama_index import ServiceContext, StorageContext, load_index_from_storage
from llama_index.callbacks import CallbackManager
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.indices.base import BaseIndex
from llama_index.indices.knowledge_graph.retrievers import KGRetrieverMode
from llama_index.llms import OpenAI
from rich.console import Console
from tqdm import tqdm

from bellek.llama_index.data_structs.data_structs import patch_kg_data_struct
from bellek.llama_index.graph_stores.kuzu import KuzuGraphStore
from bellek.llama_index.indices.knowledge_graph.base import patch_knowledge_graph_index
from bellek.llama_index.obs import make_phoenix_trace_callback_handler
from bellek.musique.constants import SKIPPED_RECORD_IDS
from bellek.utils import set_seed

err = Console(stderr=True).print

load_dotenv()

set_seed(89)


patch_kg_data_struct()
patch_knowledge_graph_index()


# model to generate embeddings for triplets
embed_model = HuggingFaceEmbedding("sentence-transformers/all-MiniLM-L6-v2")

# language model to answer questions
# llm = OpenAI(temperature=0.0, model="gpt-3.5-turbo")
llm = OpenAI(temperature=0.0, model="gpt-3.5-turbo", api_base="http://localhost:8080/v1", api_key="_")


def make_service_context(directory: Path, example_id: str):
    example_dir = directory / example_id
    example_dir.mkdir(exist_ok=True, parents=True)

    traces_filepath = example_dir / "traces.jsonl"
    traces_filepath.unlink(missing_ok=True)
    trace_callback_handler = make_phoenix_trace_callback_handler(traces_filepath)
    callback_manager = CallbackManager(handlers=[trace_callback_handler])
    return ServiceContext.from_defaults(
        llm=llm,
        embed_model=embed_model,
        callback_manager=callback_manager,
    )


def load_index(directory: Path, service_context: ServiceContext):
    db = kuzu.Database(str(directory / "kuzu"))
    graph_store = KuzuGraphStore(db)
    storage_context = StorageContext.from_defaults(persist_dir=directory / "index", graph_store=graph_store)
    return load_index_from_storage(
        storage_context,
        service_context=service_context,
        include_embeddings=True,
    )


TEXT_QA_PROMPT_USER_MSG_CONTENT = """Context information is below.
---------------------
{context_str}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {query_str}
Answer in 2-4 words: """


def make_query_engine(index: BaseIndex):
    query_engine = index.as_query_engine(
        include_text=False,
        embedding_mode="hybrid",
        retriever_mode=KGRetrieverMode.HYBRID,
        response_mode="simple_summarize",
        verbose=True,
    )
    original_text_qa_prompt = query_engine.get_prompts()["response_synthesizer:text_qa_template"]
    original_text_qa_prompt.conditionals[0][1].message_templates[1].content = TEXT_QA_PROMPT_USER_MSG_CONTENT
    query_engine.update_prompts({"response_synthesizer:text_qa_template": original_text_qa_prompt})
    return query_engine


def answer_questions(query_engine, example):
    sub_questions = [item["question"] for item in example["question_decomposition"]]
    hop1_question = sub_questions[0]
    hop1_answer = query_engine.query(hop1_question).response
    example["question_decomposition"][0]["answer"] = hop1_answer
    hop2_question = sub_questions[1].replace("#1", hop1_answer)
    hop2_answer = query_engine.query(hop2_question).response
    example["question_decomposition"][1]["answer"] = hop2_answer
    return example


def main(
    dataset_file: Path = typer.Option(...),
    knowledge_graph_directory: Path = typer.Option(...),
    out: Path = typer.Option(...),
    ignore_errors: bool = typer.Option(False),
    resume: bool = typer.Option(False),
):
    out.mkdir(exist_ok=True, parents=True)

    with open(dataset_file) as src:
        lines = src.readlines()
    
    for line in tqdm(lines):
        example = json.loads(line)
        example_id = example["id"]
        
        if example_id in SKIPPED_RECORD_IDS:
            continue

        example_out_dir = out / example_id
        if resume and (example_out_dir / "answer.json").exists():
            err(f"Skipping the sample {example_id} because it already exists.")
            continue

        shutil.rmtree(example_out_dir, ignore_errors=True)

        err(f"Setting up query engine for {example_id}")
        service_context = make_service_context(out, example_id)
        try:
            index = load_index(knowledge_graph_directory / example_id, service_context)
        except Exception as exc:
            err(f"Failed to load the knowledge graph for sample {example_id}.\n{exc}")
            if ignore_errors:
                continue
            raise exc

        try:
            query_engine = make_query_engine(index)
            err(f"Answering the question in the sample {example_id}")
            example_answered = answer_questions(query_engine, example)
            with open(example_out_dir / "answer.json", "w") as dst:
                dst.write(json.dumps(example_answered, ensure_ascii=False, indent=2))
        except Exception as exc:
            err(f"Failed to answer the question for sample {example_id}.\n{exc}")
            if ignore_errors:
                continue
            raise exc

    with open(out / "timestamp.txt", "w") as f:
        f.write(datetime.now().isoformat())

if __name__ == "__main__":
    typer.run(main)
