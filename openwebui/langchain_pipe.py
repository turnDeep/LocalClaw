"""
title: Official Docs RAG Pipe
author: OpenWebUI User
description: Queries local official documents using LangChain v1.
version: 1.0.0
"""

import sys
import os
from pydantic import BaseModel, Field

# Add the directory containing the rag_system to python path
sys.path.append("/app/backend/rag_system")

# Import the query function (assuming it can be imported, otherwise we exec it)
try:
    from query import query_rag
except ImportError:
    # Fallback or placeholder if dependencies aren't loaded yet during UI init
    query_rag = None

class Pipe:
    class Valves(BaseModel):
        pass

    def __init__(self):
        self.valves = self.Valves()

    def pipe(self, body: dict, __user__: dict) -> str:
        if not query_rag:
            return "Error: RAG system modules not found. Please check container setup."

        user_message = body.get("messages", [])[-1].get("content", "")
        print(f"Pipe received query: {user_message}")

        try:
            # Change working dir to where chromadb is expected if necessary,
            # or ensure query.py handles absolute paths.
            # In our case, query.py uses "chroma_db", we mounted it at /app/backend/chroma_db
            # We might need to chdir or update paths in query.py.
            # Ideally query.py uses absolute paths or we set CWD.
            original_cwd = os.getcwd()
            os.chdir("/app/backend/rag_system")

            response = query_rag(user_message)

            os.chdir(original_cwd)
            return response
        except Exception as e:
            return f"Error executing RAG: {str(e)}"
