import sys
import argparse
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Configuration
CHROMA_DIR = "chroma_db"
EMBEDDING_MODEL = "kun432/cl-nagoya-ruri-large"
LLM_MODEL = "gemma3:27b" # Or "gpt-oss:20b"

def query_rag(query_text: str):
    """
    Queries the RAG system and returns the answer.
    """
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )

    # Retrieve top 5 chunks
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    # Define the prompt template
    template = """あなたは日本の公文書（通達など）に精通したアシスタントです。
以下の「コンテキスト」のみに基づいて、質問に日本語で丁寧に答えてください。
コンテキストに答えが含まれていない場合は、「提供された文書には情報がありません」と答えてください。

コンテキスト:
{context}

質問:
{question}
"""
    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatOllama(model=LLM_MODEL)

    def format_docs(docs):
        return "\n\n".join([d.page_content for d in docs])

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    print(f"--- Querying for: {query_text} ---")
    try:
        response = rag_chain.invoke(query_text)
        print(response)
        return response
    except Exception as e:
        print(f"Error: {e}")
        return str(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='RAG Query Tool')
    parser.add_argument('query', type=str, help='The question to ask')
    args = parser.parse_args()
    query_rag(args.query)
