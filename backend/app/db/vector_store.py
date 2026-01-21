"""
VectorStoreManager module for SentinAI.
Handles vector storage and similarity search using Chroma and Google Embeddings.
"""

import os
from typing import Dict, List, Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings


class VectorStoreManager:
    """
    Production-ready vector store manager for document storage
    and semantic similarity search using Chroma and Google AI embeddings.
    """

    DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
    COLLECTION_NAME = "sentinai_documents"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the VectorStoreManager.
        
        Args:
            api_key: Google API key for embeddings. If None, uses GOOGLE_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.embeddings: Optional[GoogleGenerativeAIEmbeddings] = None
        self.vector_store: Optional[Chroma] = None
        self._ensure_data_dir()

    def _ensure_data_dir(self) -> None:
        """Ensure the data directory exists."""
        os.makedirs(self.DATA_DIR, exist_ok=True)

    def _get_persist_directory(self) -> str:
        """Get the full path to the vector store persistence directory."""
        return os.path.join(self.DATA_DIR, "chroma_db")

    def initialize(self) -> Dict[str, str]:
        """
        Initialize the embeddings model and vector store.
        
        Returns:
            Dictionary with status and message.
        """
        if not self.api_key:
            return {
                "status": "error",
                "message": "Google API key not provided. Set GOOGLE_API_KEY environment variable."
            }

        try:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=self.api_key
            )

            persist_directory = self._get_persist_directory()
            self.vector_store = Chroma(
                collection_name=self.COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=persist_directory
            )

            return {
                "status": "success",
                "message": f"Vector store initialized at {persist_directory}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to initialize vector store: {str(e)}"
            }

    def add_documents(self, texts: List[str], metadatas: Optional[List[Dict]] = None) -> Dict[str, any]:
        """
        Add documents to the vector store.
        
        Args:
            texts: List of text strings to add.
            metadatas: Optional list of metadata dictionaries for each text.
            
        Returns:
            Dictionary containing:
                - status: 'success' or 'error'
                - count: Number of documents added (on success)
                - message: Status or error message
        """
        if not self.vector_store:
            init_result = self.initialize()
            if init_result["status"] == "error":
                return init_result

        if not texts:
            return {
                "status": "error",
                "message": "No texts provided to add"
            }

        try:
            documents = []
            for i, text in enumerate(texts):
                metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
                documents.append(Document(page_content=text, metadata=metadata))

            self.vector_store.add_documents(documents)

            return {
                "status": "success",
                "count": len(documents),
                "message": f"Successfully added {len(documents)} documents"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to add documents: {str(e)}"
            }

    def similarity_search(self, query: str, k: int = 5) -> Dict[str, any]:
        """
        Perform similarity search on the vector store.
        
        Args:
            query: The search query text.
            k: Number of results to return. Defaults to 5.
            
        Returns:
            Dictionary containing:
                - status: 'success' or 'error'
                - results: List of matching documents with scores (on success)
                - message: Error message (on error)
        """
        if not self.vector_store:
            init_result = self.initialize()
            if init_result["status"] == "error":
                return init_result

        if not query or not query.strip():
            return {
                "status": "error",
                "message": "Query cannot be empty"
            }

        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)

            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": round(float(score), 4)
                })

            return {
                "status": "success",
                "results": formatted_results,
                "count": len(formatted_results)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Similarity search failed: {str(e)}"
            }

    def delete_collection(self) -> Dict[str, str]:
        """
        Delete the entire collection from the vector store.
        
        Returns:
            Dictionary with status and message.
        """
        try:
            if self.vector_store:
                self.vector_store.delete_collection()
                self.vector_store = None
            return {
                "status": "success",
                "message": "Collection deleted successfully"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to delete collection: {str(e)}"
            }
