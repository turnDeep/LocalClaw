FROM node:22-bookworm

# Install Python and build dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install OpenClaw globally
RUN npm install -g openclaw@latest

# Setup Python environment for LangChain RAG
COPY rag_system/requirements.txt /tmp/requirements.txt
RUN pip3 install --break-system-packages -r /tmp/requirements.txt

# Create workspace directory
WORKDIR /root/.openclaw/workspace

# Expose Gateway port
EXPOSE 18789

# Start the gateway
CMD ["openclaw", "gateway", "--port", "18789"]
