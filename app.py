import streamlit as st
import io
import os
import ollama
from pathlib import Path
from rag_module import RagModule
from llama_index.core import Document
from utils.file_reader_toolkit import FileReaderToolkit
from utils.llm_loader import load_ollama_model
from utils.parse_metada import parse_metadata
# Constants for session state keys
SESSION_RAG_MODULE_KEY = "rag_module_instance"
SESSION_CURRENT_INDEX_KEY = "current_index"

APP_DIR = Path(__file__).parent.resolve()
INDICES_DIR = APP_DIR / "indices"


# Instantiate File Reader
reader_toolkit = FileReaderToolkit()

def ollama_model_sidebar():
    with st.sidebar:
        st.header("Select Ollama Model")
        model_name = st.selectbox(
            label="Select model",
            options=[
                model.get("name").split(":")[0]
                for model in ollama.list()["models"] if model.get("name")
            ],
            index=0,
            label_visibility="hidden"
        )
    return model_name


def initialize_session_state():
    """Initialize the session state variables."""
    if SESSION_RAG_MODULE_KEY not in st.session_state:
        st.session_state[SESSION_RAG_MODULE_KEY] = None
    if SESSION_CURRENT_INDEX_KEY not in st.session_state:
        st.session_state[SESSION_CURRENT_INDEX_KEY] = None
    if "model_name" not in st.session_state:
        st.session_state["model_name"] = None


def build_document(uploaded_file):
    """Build a Document object from an uploaded file."""
    file_data = uploaded_file.getvalue()
    file_stream = io.BytesIO(file_data)
    file_stream.name = uploaded_file.name
    try:
        file_content = reader_toolkit.get_content(file=file_stream)
        file_name = file_stream.name
        file_type = reader_toolkit.current_file_type
        document = Document(
            text=file_content,
            metadata={"file_name": file_name, "file_type": file_type},
        )
        return document
    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")
        return None


def insert_text_section():
    """UI section for inserting text."""
    st.header("Insert Text")
    with st.form("insert_text_form"):
        input_text = st.text_area("Input Text")
        metadata_input = st.text_input("Metadata (Optional)")
        metadata = parse_metadata(metadata_input=metadata_input)

        submitted_text = st.form_submit_button("Insert Text")

        if submitted_text:
            if input_text:
                try:
                    st.session_state[SESSION_RAG_MODULE_KEY].insert_text(
                        input_text, metadata
                    )
                    st.success("Text inserted successfully.")
                except Exception as e:
                    st.error(f"An error occurred while inserting text: {e}")
            else:
                st.error("Please enter input text.")


def upload_file_section():
    """UI section for uploading files."""
    st.header("Upload Files")
    uploaded_file = st.file_uploader("Upload a File")

    if uploaded_file:
        document = build_document(uploaded_file)
        if document:
            try:
                file_name = document.metadata.get("file_name")
                st.session_state[SESSION_RAG_MODULE_KEY].insert_document(document)
                st.success(f"File '{file_name}' added successfully.")
                # Update current index if not set
                if st.session_state.get(SESSION_CURRENT_INDEX_KEY) is None:
                    st.session_state[SESSION_CURRENT_INDEX_KEY] = file_name
            except Exception as e:
                st.error(f"An error occurred while adding the document: {e}")


def index_management_sidebar():
    """Sidebar for index management."""
    with st.sidebar:
        st.header("Index Management")

        # Ensure INDICES_DIR exists
        INDICES_DIR.mkdir(parents=True, exist_ok=True)

        index_options = os.listdir(INDICES_DIR)
        if index_options:
            persist_dir_name = st.selectbox("Select Index", index_options)
        else:
            st.info("No indices available.")
            persist_dir_name = None

        load_index_button = st.button("Load Selected Index")
        save_index_button = st.button("Save Current Index")
        flush_index_button = st.button("Flush Current Index")
        saving_dir_name = st.text_input(
            "Enter name to save index", value=persist_dir_name or ""
        )

        if load_index_button:
            if persist_dir_name:
                persist_dir_path = INDICES_DIR / persist_dir_name
                try:
                    st.session_state[SESSION_RAG_MODULE_KEY].load_existing_index(
                        str(persist_dir_path)
                    )
                    st.session_state[SESSION_CURRENT_INDEX_KEY] = str(persist_dir_path)
                    st.success(f"Index loaded from '{persist_dir_path}'.")
                except Exception as e:
                    st.error(f"An error occurred while loading the index: {e}")
            else:
                st.error("Please select an index to load.")

        if save_index_button:
            if saving_dir_name:
                saving_dir_path = INDICES_DIR / saving_dir_name
                try:
                    st.session_state[SESSION_RAG_MODULE_KEY].save_index(
                        str(saving_dir_path)
                    )
                    st.success(f"Index saved to '{saving_dir_path}'.")
                except Exception as e:
                    st.error(f"An error occurred while saving the index: {e}")
            else:
                st.error("Please enter a name to save the index.")

        if flush_index_button:
            try:
                st.session_state[SESSION_RAG_MODULE_KEY].flush()
                st.session_state[SESSION_CURRENT_INDEX_KEY] = None
                st.success("Index flushed and reinitialized successfully.")
            except Exception as e:
                st.error(f"An error occurred while flushing the index: {e}")

        st.write(
            f"**Current Index:** {st.session_state.get(SESSION_CURRENT_INDEX_KEY, 'None')}"
        )


def query_section():
    """UI section for querying the index."""
    st.header("Chat with the Index")
    query = st.chat_input("Enter your query")

    if query:
        st.chat_message("user").write(query)
        try:
            result = st.session_state[SESSION_RAG_MODULE_KEY].query(query)
            st.chat_message("assistant").write_stream(result)
        except Exception as e:
            st.error(f"An error occurred while processing the query: {e}")


def main():
    # Initialize session state
    initialize_session_state()

    # Ollama model sidebar
    model_name = ollama_model_sidebar()

    # Check if model_name has changed
    if st.session_state["model_name"] != model_name:
        # Load new LLM instance
        LLM_INSTANCE = load_ollama_model(model_name=model_name)
        if st.session_state[SESSION_RAG_MODULE_KEY] is None:
            # Create new RagModule instance with the new LLM
            st.session_state[SESSION_RAG_MODULE_KEY] = RagModule(llm=LLM_INSTANCE)
        else:
            # Update the llm in RagModule without affecting the index
            st.session_state[SESSION_RAG_MODULE_KEY].llm = LLM_INSTANCE
        # Update the model_name in session state
        st.session_state["model_name"] = model_name

    # Display the title
    st.title("RAG Module UI")

    # Index management sidebar
    index_management_sidebar()

    # Insert text section
    insert_text_section()

    # Upload file section
    upload_file_section()

    # Query section
    query_section()


if __name__ == "__main__":
    main()
