FROM ghcr.io/open-webui/open-webui:main

# Install LangChain and RAG dependencies
COPY rag_system/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
