# RAG Module

In this repository, we build the `RagModule` class, a wrapper around `llama-index` that implements Retrieval Augmented Generation (RAG). We provide a `Streamlit` UI for the `RagModule` that uses `Ollama`, allowing users to input text or upload documents to build an index and query it through an interactive chat interface.


## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Running the Application](#running-the-application)
  - [Index Management](#index-management)
  - [Chat Interface](#chat-interface)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Features

- **Insert Text**: Manually input text and optional metadata to build your index.
- **Upload Documents**: Drag and drop files (PDFs, Word documents, Excel files, etc.) to add to your index.
- **Index Management**: Save, load, and flush indices for persistent data storage.
- **Chat Interface**: Interactively query your index using a chat-based interface.
- **Customizable LLM**: Easily switch between differents LLMs using Ollama (or other provider).

## Installation

### Prerequisites

- Python 3.11 [tested]
- [pip](https://pip.pypa.io/en/stable/installation/)
- [Git](https://git-scm.com/downloads)

### Clone the Repository

```bash
git clone https://github.com/hbacard/rag-module.git
cd rag-module
```

### Create a Virtual Environment

It's recommended to use a virtual environment to manage dependencies.

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install Ollama and pull LLM

- Install [Ollama](https://ollama.ai/)
- Pull your favorite LLM using `ollama pull model_name`, e.g. `ollama pull llama3.1`.

### Download the Embedding Model
#### First install git lfs (large file storage):
 - `curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash `
 - `sudo apt install git-lfs && sudo apt-get update` 
 - `git lfs install` 
 - Check for installation `git-lfs --version`
#### Download the embedding model (bge-m3 for multilingual embeddings):
```sh
git clone https://huggingface.co/BAAI/bge-m3 && rm -rf bge-m3/.git
```

## Usage

### Running the Application

Start the Streamlit application by running:

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

**Note**: If an error occurs, try to deactivate and activate the environment and run again `streamlit run app.py`
### Index Management

Use the sidebar to manage your indices:

- **Select Index**: Choose an existing index to load.
- **Load Selected Index**: Load the chosen index into the application.
- **Save Current Index**: Save the current index with a specified name.
- **Flush Current Index**: Clear the current index and start fresh.
- **Enter name to save index**: Provide a name for saving the index.




## Dependencies

- [llama-index](https://github.com/run-llama/llama_index)
- [Streamlit](https://streamlit.io/)
- [Ollama](https://ollama.com)
- Other dependencies as listed in `requirements.txt`.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## Troubleshooting

- **Model Loading Errors**: Verify that the model is pulled with Ollama
- **Dependency Issues**: Run `pip install -r requirements.txt` to ensure all dependencies are installed.
- **Virtual environment Issues**: Sometimes it is best to deactivate and reactivate the environment after installing the dependencies.