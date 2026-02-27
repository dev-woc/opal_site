"""
Vector Store for RAG Embeddings

Manages vector database for semantic search of pedagogical content.
Uses ChromaDB for persistent storage and efficient retrieval.
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import os
from pathlib import Path
import hashlib
import time


class VectorStore:
    """
    Manages vector embeddings and semantic search for RAG system.

    Features:
    - Persistent ChromaDB storage
    - Automatic embedding generation
    - Semantic similarity search
    - Metadata filtering
    - Query caching for performance
    """

    def __init__(
        self,
        collection_name: str = "structured_literacy",
        persist_directory: str = "./app/rag/chroma_db",
        cache_enabled: bool = True
    ):
        """
        Initialize the vector store

        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory for persistent storage
            cache_enabled: Enable query caching
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.cache_enabled = cache_enabled
        self._query_cache: Dict[str, Dict[str, Any]] = {}

        # Create persist directory if it doesn't exist
        Path(persist_directory).mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Structured Literacy pedagogical knowledge base"}
            )

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Add documents to the vector store

        Args:
            documents: List of text documents to add
            metadatas: Optional metadata for each document
            ids: Optional custom IDs for documents

        Returns:
            Dictionary with operation status
        """
        if not documents:
            return {"success": False, "error": "No documents provided"}

        # Generate IDs if not provided
        if ids is None:
            ids = [self._generate_doc_id(doc, i) for i, doc in enumerate(documents)]

        # Ensure metadatas match document count
        if metadatas is None:
            metadatas = [{}] * len(documents)

        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            # Clear cache when new documents are added
            if self.cache_enabled:
                self._query_cache.clear()

            return {
                "success": True,
                "documents_added": len(documents),
                "collection_size": self.collection.count()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        relevance_threshold: float = 0.0
    ) -> Dict[str, Any]:
        """
        Query the vector store for relevant documents

        Args:
            query_text: The search query
            n_results: Number of results to return
            where: Optional metadata filter
            relevance_threshold: Minimum similarity score (0-1)

        Returns:
            Dictionary with query results
        """
        # Check cache first
        cache_key = self._generate_cache_key(query_text, n_results, where)
        if self.cache_enabled and cache_key in self._query_cache:
            cached_result = self._query_cache[cache_key]
            cached_result["cached"] = True
            return cached_result

        try:
            start_time = time.time()

            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where
            )

            query_time = time.time() - start_time

            # Process results
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            ids = results.get("ids", [[]])[0]

            # Convert distances to similarity scores (ChromaDB uses L2 distance)
            # Similarity = 1 / (1 + distance)
            similarities = [1 / (1 + d) for d in distances]

            # Filter by relevance threshold
            filtered_results = []
            for i, similarity in enumerate(similarities):
                if similarity >= relevance_threshold:
                    filtered_results.append({
                        "document": documents[i],
                        "metadata": metadatas[i],
                        "id": ids[i],
                        "similarity": similarity,
                        "distance": distances[i]
                    })

            result = {
                "success": True,
                "query": query_text,
                "results": filtered_results,
                "total_results": len(filtered_results),
                "query_time_ms": round(query_time * 1000, 2),
                "cached": False
            }

            # Cache the result
            if self.cache_enabled:
                self._query_cache[cache_key] = result

            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query_text
            }

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection

        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            return {
                "success": True,
                "collection_name": self.collection_name,
                "document_count": count,
                "cache_size": len(self._query_cache),
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def clear_cache(self) -> None:
        """Clear the query cache"""
        self._query_cache.clear()

    def reset_collection(self) -> Dict[str, Any]:
        """
        Delete and recreate the collection (use with caution!)

        Returns:
            Dictionary with operation status
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Structured Literacy pedagogical knowledge base"}
            )
            self._query_cache.clear()

            return {
                "success": True,
                "message": "Collection reset successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _generate_doc_id(self, document: str, index: int) -> str:
        """Generate a unique ID for a document"""
        # Use hash of document content plus index
        content_hash = hashlib.md5(document.encode()).hexdigest()[:8]
        return f"doc_{index}_{content_hash}"

    def _generate_cache_key(
        self,
        query_text: str,
        n_results: int,
        where: Optional[Dict[str, Any]]
    ) -> str:
        """Generate a cache key for a query"""
        key_parts = [query_text, str(n_results), str(where)]
        return hashlib.md5("_".join(key_parts).encode()).hexdigest()
