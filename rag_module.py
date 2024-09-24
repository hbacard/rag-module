import os
from pathlib import Path
from llama_index.core import (
    Document,
    VectorStoreIndex,
    Settings,
    PromptTemplate,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from dotenv import load_dotenv

load_dotenv()
APP_DIR = Path(__file__).parent.resolve()
DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "bge-m3"
EMBEDDING_MODEL_PATH = APP_DIR / EMBEDDING_MODEL

# This a french RAG template, change the sentences [only] in your language accordingly.
TEMPLATE_RAG_FR = """
    <|start_header_id|>user<|end_header_id|>Voici un contexte entre les tags <context> de type XML.
<context>
{context_str}
</context>
En utilisant ce contexte et sans connaissances préalables, réponds à la question suivante en bon français.
Question : {query_str}<|eot_id|>
Réponse :
<|start_header_id|>assistant<|end_header_id|> 
"""


Settings.embed_model = HuggingFaceEmbedding(model_name=str(EMBEDDING_MODEL_PATH))

class RagModule:
    """
    A wrapper around llama-index to perform real-time RAG (Retrieval-Augmented Generation).

    This class provides methods for initializing the index, inserting documents and texts,
    querying the index, and saving/loading the index.

    :param llm: The large language model to use.
    :param index: The index to use or build (optional).
    :param query_engine: The query engine to use (optional).
    """

    def __init__(
        self,
        llm,
        chunk_size=DEFAULT_CHUNK_SIZE,
        chunk_overlap=DEFAULT_CHUNK_OVERLAP,
        index=None,
        query_engine=None,
    ):
        """
        Initialize the RagModule instance.

        :param llm: The large language model to use.
        :param index: The index to use or build (optional).
        :param query_engine: The query engine to use (optional).
        """
        self.llm = llm
        self.index = index
        self.query_engine = query_engine
        self.qa_template = PromptTemplate(TEMPLATE_RAG_FR)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def init_index(self):
        """
        Initialize the index if it is not already initialized.

        :return: The current instance of the RagModule class.
        """
        if self.index is None:
            self.index = VectorStoreIndex.from_documents(
                documents=[],
                transformations=[
                    SentenceSplitter(
                        chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
                    )
                ],
            )
            self.update_query_engine()
        return self

    def flush(self):
        """
        Reset and reinitialize the index.

        :return: The current instance of the RagModule class with an empty index.
        """
        self.index = None
        return self.init_index()

    def update_query_engine(self):
        """
        Update the query engine with the latest index and LLM.

        :return: The current instance of the RagModule class.
        """
        if self.index is None:
            raise ValueError("Index is not initialized. Call init_index() first.")

        self.query_engine = self.index.as_query_engine(
            llm=self.llm,
            streaming=True,
            top_k=2,
        )
        self.query_engine.update_prompts(
            {"response_synthesizer:text_qa_template": self.qa_template}
        )
        return self

    def insert_document(self, document):
        """
        Insert a document into the index and update the query engine.

        :param document: The document to be inserted.
        :return: The current instance of the RagModule class with the new document.
        """
        try:
            self.init_index()
            self.index.insert(document=document)
            self.update_query_engine()
        except Exception as e:
            print(f"Error occurred while inserting document: {e}")
        return self

    def insert_text(self, input_text, metadata={}):
        """
        Insert text into the index and update the query engine.

        :param input_text: The text to be inserted.
        :param metadata: Optional metadata dictionary for the document.
        :return: The current instance of the RagModule class with the new text.
        """

        document = Document(text=input_text, metadata=metadata)
        return self.insert_document(document=document)

    def query(self, query, print_response: bool = False):
        """
        Query the index with a given query.

        :param query: The query to be executed.
        :print_response: Optional boolean to print the result. If set to True the generator will be empty.
        :return: None
        """
        try:
            self.init_index()
            response_stream = self.query_engine.query(query)
            if print_response:
                for token in response_stream.response_gen:
                    print(token, end="", flush=True)
            return response_stream.response_gen

            #     yield token
        except Exception as e:
            print(f"Error occurred during querying: {e}")

    def save_index(self, persist_dir):
        """
        Save the current index to a specified directory.

        :param persist_dir: The path where the index should be saved.
        :return: The current instance of the RagModule class, or an error message if there is a problem with the persist_dir.
        """
        try:
            if persist_dir and self.index:
                self.index.storage_context.persist(persist_dir=persist_dir)
            else:
                raise ValueError("Either index is None or persist_dir is invalid.")
        except Exception as e:
            print(f"Error occurred while saving index: {e}")
        return self

    def load_existing_index(self, persist_dir):
        """
        Load an existing index from a specified directory.

        :param persist_dir: The path where the index should be loaded from.
        :return: The current instance of the RagModule class, or an error message if there is a problem with the persist_dir.
        """
        try:
            storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
            self.index = load_index_from_storage(storage_context=storage_context)
            self.update_query_engine()
        except Exception as e:
            print(f"Error occurred while loading index: {e}")
        return self
