"""
Vector Database for Pedagogical Rules

Stores and retrieves pedagogical rules from WRS, OG, UFLI, and FCRR
using ChromaDB with sentence embeddings.
"""

import logging
from typing import List, Dict, Any, Optional
import chromadb

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    # Fallback: use simple embedding
    SentenceTransformer = None

logger = logging.getLogger(__name__)


class VectorDatabase:
    """
    Vector database for storing and retrieving pedagogical rules
    """

    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize vector database

        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        logger.info(f"Initializing VectorDatabase at {persist_directory}")

        # Set ChromaDB cache to project directory to avoid permission issues
        import os
        os.environ["CHROMA_CACHE_DIR"] = os.path.join(persist_directory, ".cache")

        # Initialize ChromaDB client (chromadb 1.x API)
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Initialize embedding model
        if HAS_SENTENCE_TRANSFORMERS:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Loaded sentence-transformers embedding model: all-MiniLM-L6-v2")
        else:
            self.embedding_model = None
            logger.warning("sentence-transformers not available, using ChromaDB default embeddings")

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="pedagogical_rules",
            metadata={"description": "WRS, OG, UFLI, and FCRR pedagogical rules"}
        )

        logger.info("VectorDatabase initialized successfully")

    def add_rule(
        self,
        rule_id: str,
        rule_text: str,
        source: str,
        category: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a pedagogical rule to the vector database

        Args:
            rule_id: Unique identifier for the rule
            rule_text: Full text of the rule
            source: Source framework (WRS, OG, UFLI, FCRR)
            category: Category of rule (phonics, morphology, syntax, etc.)
            metadata: Additional metadata
        """
        # Prepare metadata
        rule_metadata = {
            "source": source,
            "category": category,
            **(metadata or {})
        }

        # Add to collection (ChromaDB will auto-generate embeddings if not provided)
        if self.embedding_model:
            embedding = self.embedding_model.encode(rule_text).tolist()
            self.collection.add(
                ids=[rule_id],
                embeddings=[embedding],
                documents=[rule_text],
                metadatas=[rule_metadata]
            )
        else:
            # Let ChromaDB use default embeddings
            self.collection.add(
                ids=[rule_id],
                documents=[rule_text],
                metadatas=[rule_metadata]
            )

        logger.debug(f"Added rule {rule_id} from {source} to vector database")

    def add_rules_batch(self, rules: List[Dict[str, Any]]) -> None:
        """
        Add multiple rules to the vector database

        Args:
            rules: List of rule dictionaries with keys:
                   - rule_id
                   - rule_text
                   - source
                   - category
                   - metadata (optional)
        """
        logger.info(f"Adding {len(rules)} rules to vector database")

        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for rule in rules:
            ids.append(rule["rule_id"])
            documents.append(rule["rule_text"])

            if self.embedding_model:
                # Generate embedding
                embedding = self.embedding_model.encode(rule["rule_text"]).tolist()
                embeddings.append(embedding)

            # Prepare metadata
            metadata = {
                "source": rule["source"],
                "category": rule["category"],
                **rule.get("metadata", {})
            }
            metadatas.append(metadata)

        # Batch add to collection
        if self.embedding_model:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
        else:
            # Let ChromaDB use default embeddings
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )

        logger.info(f"Successfully added {len(rules)} rules to vector database")

    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        source_filter: Optional[str] = None,
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant pedagogical rules

        Args:
            query: Query text (e.g., "rules for teaching short vowels")
            n_results: Number of results to return
            source_filter: Filter by source (WRS, OG, UFLI, FCRR)
            category_filter: Filter by category

        Returns:
            List of retrieved rules with metadata
        """
        logger.debug(f"Retrieving rules for query: {query}")

        # Build where clause for filtering
        where = {}
        if source_filter:
            where["source"] = source_filter
        if category_filter:
            where["category"] = category_filter

        # Query collection
        if self.embedding_model:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where if where else None
            )
        else:
            # Use query text directly (ChromaDB will handle embedding)
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where if where else None
            )

        # Format results
        retrieved_rules = []
        for i in range(len(results["ids"][0])):
            retrieved_rules.append({
                "rule_id": results["ids"][0][i],
                "rule_text": results["documents"][0][i],
                "source": results["metadatas"][0][i]["source"],
                "category": results["metadatas"][0][i]["category"],
                "distance": results["distances"][0][i] if "distances" in results else None,
                "metadata": results["metadatas"][0][i]
            })

        logger.debug(f"Retrieved {len(retrieved_rules)} rules")
        return retrieved_rules

    def get_rule_by_id(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific rule by ID

        Args:
            rule_id: Rule identifier

        Returns:
            Rule dictionary or None if not found
        """
        try:
            result = self.collection.get(ids=[rule_id])
            if result["ids"]:
                return {
                    "rule_id": result["ids"][0],
                    "rule_text": result["documents"][0],
                    "metadata": result["metadatas"][0]
                }
        except Exception as e:
            logger.error(f"Error retrieving rule {rule_id}: {e}")

        return None

    def count_rules(self) -> int:
        """
        Get total number of rules in database

        Returns:
            Number of rules
        """
        return self.collection.count()

    def clear(self) -> None:
        """
        Clear all rules from database
        """
        logger.warning("Clearing all rules from vector database")
        self.client.delete_collection("pedagogical_rules")
        self.collection = self.client.get_or_create_collection(
            name="pedagogical_rules",
            metadata={"description": "WRS, OG, UFLI, and FCRR pedagogical rules"}
        )
        logger.info("Vector database cleared")
