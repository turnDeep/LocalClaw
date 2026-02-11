import os
import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# Configuration
DOCS_DIR = "docs"
CHROMA_DIR = "chroma_db"
EMBEDDING_MODEL = "kun432/cl-nagoya-ruri-large"

def ingest_documents():
    """
    Ingests PDF documents from the docs directory, splits them using Japanese-optimized separators,
    and stores the embeddings in ChromaDB.
    """
    print(f"Loading documents from {DOCS_DIR}...")
    pdf_files = glob.glob(os.path.join(DOCS_DIR, "**/*.pdf"), recursive=True)

    if not pdf_files:
        print("No PDF files found.")
        return

    documents = []
    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file}")
        try:
            loader = PyPDFLoader(pdf_file)
            documents.extend(loader.load())
        except Exception as e:
            print(f"Error loading {pdf_file}: {e}")

    # "Tsutatsu" style optimized separators
    separators = ["\n\n", "\n", "記", "第", "。", "、", " ", ""]

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=separators,
        keep_separator=True,
        is_separator_regex=False,
    )

    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")

    print(f"Creating embeddings using {EMBEDDING_MODEL}...")
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

    # Create/Update Vector Store
    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )
    vectorstore.add_documents(documents=chunks)

    print("Ingestion complete. Vector store updated.")

if __name__ == "__main__":
    ingest_documents()
