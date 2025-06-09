# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from pathlib import Path
from dotenv import load_dotenv, set_key

# Load environment first!
env_file_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_file_path)

# Now safely access env vars
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
if not PROJECT_ID:
    raise ValueError("GOOGLE_CLOUD_PROJECT is not set in your .env file")

# Initialize Vertex AI with project from environment
import vertexai
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.expanduser("~/.config/gcloud/application_default_credentials.json")
print(f"[DEBUG] Using project: {PROJECT_ID}")
vertexai.init(project=PROJECT_ID, location="us-central1")

from vertexai import rag

# Define the path to the .env file
env_file_path = Path(__file__).parent.parent.parent / ".env"
print(env_file_path)

# Load environment variables from the specified .env file
load_dotenv(dotenv_path=env_file_path)

corpus_name = os.getenv("BQML_RAG_CORPUS_NAME")

display_name = "bqml_referenceguide_corpus"

paths = [
    "gs://cloud-samples-data/adk-samples/data-science/bqml"
]  # Supports Google Cloud Storage and Google Drive Links


def create_RAG_corpus():
    # Create RagCorpus
    # Configure embedding model, for example "text-embedding-005".
    embedding_model_config = rag.RagEmbeddingModelConfig(
        vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
            publisher_model="publishers/google/models/text-embedding-005"
        )
    )

    backend_config = rag.RagVectorDbConfig(
        rag_embedding_model_config=embedding_model_config
    )

    # Explicitly set the project ID in the corpus name
    corpus_name = f"projects/{PROJECT_ID}/locations/us-central1/ragCorpora/bqml_referenceguide_corpus"
    
    bqml_corpus = rag.create_corpus(
        name=corpus_name,
        display_name=display_name,
        backend_config=backend_config,
    )

    write_to_env(bqml_corpus.name)

    return bqml_corpus.name


def ingest_files(corpus_name):

    transformation_config = rag.TransformationConfig(
        chunking_config=rag.ChunkingConfig(
            chunk_size=512,
            chunk_overlap=100,
        ),
    )

    rag.import_files(
        corpus_name,
        paths,
        transformation_config=transformation_config,  # Optional
        max_embedding_requests_per_min=1000,  # Optional
    )

    # List the files in the rag corpus
    rag.list_files(corpus_name)


def rag_response(query: str) -> str:
    """Retrieves contextually relevant information from a RAG corpus.

    Args:
        query (str): The query string to search within the corpus.

    Returns:
        vertexai.rag.RagRetrievalQueryResponse: The response containing retrieved
        information from the corpus.
    """
    corpus_name = os.getenv("BQML_RAG_CORPUS_NAME")

    rag_retrieval_config = rag.RagRetrievalConfig(
        top_k=3,  # Optional
        filter=rag.Filter(vector_distance_threshold=0.5),  # Optional
    )
    response = rag.retrieval_query(
        rag_resources=[
            rag.RagResource(
                rag_corpus=corpus_name,
            )
        ],
        text=query,
        rag_retrieval_config=rag_retrieval_config,
    )
    return str(response)


def write_to_env(corpus_name):
    """Writes the corpus name to the specified .env file.

    Args:
        corpus_name: The name of the corpus to write.
    """

    load_dotenv(env_file_path)  # Load existing variables if any

    # Set the key-value pair in the .env file
    set_key(env_file_path, "BQML_RAG_CORPUS_NAME", corpus_name)
    print(f"BQML_RAG_CORPUS_NAME '{corpus_name}' written to {env_file_path}")


if __name__ == "__main__":
    # rag_corpus = rag.list_corpora()

    corpus_name = os.getenv("BQML_RAG_CORPUS_NAME")

    print("Creating the corpus.")
    corpus_name = create_RAG_corpus()
    print(f"Corpus name: {corpus_name}")

    print(f"Importing files to corpus: {corpus_name}")
    ingest_files(corpus_name)
    print(f"Files imported to corpus: {corpus_name}")
