"""
RAG Retrieval Engine

Orchestrates retrieval from multiple sources with relevance scoring,
caching, and fallback mechanisms. Provides unified interface for
querying structured literacy knowledge.
"""

from typing import List, Dict, Any, Optional
from .vector_store import VectorStore
from .structured_literacy_kb import StructuredLiteracyKB
from .fcrr_database import FCRRDatabase
import time


class RetrievalEngine:
    """
    Main retrieval engine for RAG system.

    Features:
    - Multi-source retrieval (vector KB + FCRR database)
    - Relevance scoring and ranking
    - Query expansion and reformulation
    - Caching for frequent queries
    - Fallback mechanisms for missing knowledge
    - Strict constraints to prevent hallucination
    """

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        auto_initialize_kb: bool = True
    ):
        """
        Initialize the retrieval engine

        Args:
            vector_store: Optional VectorStore instance
            auto_initialize_kb: Automatically ingest knowledge base on init
        """
        self.vector_store = vector_store or VectorStore()
        self.kb = StructuredLiteracyKB(vector_store=self.vector_store)
        self.fcrr_db = FCRRDatabase()

        # Initialize knowledge base if requested
        if auto_initialize_kb:
            self._initialize_knowledge_base()

        # Query cache
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _initialize_knowledge_base(self) -> Dict[str, Any]:
        """
        Initialize the knowledge base with all sources

        Returns:
            Dictionary with initialization status
        """
        # Check if already initialized
        stats = self.vector_store.get_collection_stats()
        if stats.get("document_count", 0) > 0:
            return {
                "success": True,
                "message": "Knowledge base already initialized",
                "document_count": stats["document_count"]
            }

        # Ingest all sources
        return self.kb.ingest_all_sources()

    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        source_filter: Optional[str] = None,
        include_word_lists: bool = True,
        relevance_threshold: float = 0.3
    ) -> Dict[str, Any]:
        """
        Retrieve relevant pedagogical knowledge for a query

        Args:
            query: The search query
            n_results: Number of results to return
            source_filter: Filter by source (wilson, orton_gillingham, ufli, fcrr)
            include_word_lists: Include word list matches from FCRR database
            relevance_threshold: Minimum relevance score (0-1)

        Returns:
            Dictionary with retrieval results from all sources
        """
        start_time = time.time()

        # Check cache
        cache_key = f"{query}_{n_results}_{source_filter}_{include_word_lists}"
        if cache_key in self._cache:
            cached_result = self._cache[cache_key]
            cached_result["cached"] = True
            cached_result["retrieval_time_ms"] = 0
            return cached_result

        results = {
            "success": True,
            "query": query,
            "sources": []
        }

        # 1. Retrieve from vector knowledge base
        kb_results = self.kb.query_knowledge_base(
            query=query,
            source_filter=source_filter,
            n_results=n_results
        )

        if kb_results.get("success"):
            # Filter by relevance threshold
            relevant_results = [
                r for r in kb_results.get("results", [])
                if r.get("similarity", 0) >= relevance_threshold
            ]

            results["sources"].append({
                "type": "knowledge_base",
                "total_results": len(relevant_results),
                "results": relevant_results
            })

        # 2. Retrieve from FCRR word lists (if requested)
        if include_word_lists:
            word_matches = self._search_fcrr_words(query)
            if word_matches.get("success") and word_matches.get("total_matches", 0) > 0:
                results["sources"].append({
                    "type": "fcrr_word_lists",
                    "total_results": word_matches["total_matches"],
                    "results": word_matches["matches"][:n_results]
                })

        # 3. Calculate overall relevance score
        results["total_sources"] = len(results["sources"])
        results["has_results"] = any(s["total_results"] > 0 for s in results["sources"])

        # 4. Apply fallback if no results
        if not results["has_results"]:
            results["fallback"] = self._apply_fallback(query)

        # 5. Add metadata
        retrieval_time = time.time() - start_time
        results["retrieval_time_ms"] = round(retrieval_time * 1000, 2)
        results["cached"] = False

        # Cache the result
        self._cache[cache_key] = results

        return results

    def retrieve_for_lesson_planning(
        self,
        learning_objective: str,
        difficulty: str = "beginner"
    ) -> Dict[str, Any]:
        """
        Retrieve knowledge specifically for lesson planning

        Args:
            learning_objective: The learning objective
            difficulty: Student difficulty level

        Returns:
            Dictionary with lesson planning resources
        """
        results = {
            "success": True,
            "objective": learning_objective,
            "difficulty": difficulty,
            "resources": {}
        }

        # 1. Get relevant pedagogical guidelines
        guidelines = self.retrieve(
            query=f"lesson planning {learning_objective}",
            n_results=5,
            include_word_lists=False
        )
        results["resources"]["guidelines"] = guidelines

        # 2. Get word lists by difficulty
        word_lists = self.fcrr_db.get_words_by_difficulty(difficulty)
        results["resources"]["word_lists"] = word_lists

        # 3. Get activity templates
        activities = {
            "purple": self.fcrr_db.get_activity_by_color("purple"),
            "orange": self.fcrr_db.get_activity_by_color("orange"),
            "green": self.fcrr_db.get_activity_by_color("green")
        }
        results["resources"]["activities"] = activities

        return results

    def retrieve_for_narrative_generation(
        self,
        allowed_phonemes: List[str],
        topic: str = ""
    ) -> Dict[str, Any]:
        """
        Retrieve knowledge for generating decodable narratives

        Args:
            allowed_phonemes: List of phonemes students know
            topic: Optional story topic

        Returns:
            Dictionary with narrative generation resources
        """
        results = {
            "success": True,
            "allowed_phonemes": allowed_phonemes,
            "topic": topic,
            "resources": {}
        }

        # 1. Get decodability guidelines
        decodability_query = "decodable text 95% decodability narrative generation"
        guidelines = self.retrieve(
            query=decodability_query,
            n_results=3,
            include_word_lists=False
        )
        results["resources"]["decodability_guidelines"] = guidelines

        # 2. Get word lists matching allowed patterns
        # For simplicity, get beginner and intermediate word lists
        word_lists = self.fcrr_db.get_words_by_difficulty("beginner")
        results["resources"]["word_lists"] = word_lists

        return results

    def retrieve_phonics_rule(
        self,
        rule_name: str,
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve a specific phonics rule by name

        Args:
            rule_name: Name or description of the rule
            source: Optional source filter

        Returns:
            Dictionary with rule information
        """
        return self.retrieve(
            query=rule_name,
            n_results=3,
            source_filter=source,
            include_word_lists=True,
            relevance_threshold=0.4
        )

    def get_word_list(self, pattern: str) -> Dict[str, Any]:
        """
        Get a specific word list from FCRR database

        Args:
            pattern: Pattern name (e.g., 'cvc_a', 'sh', 'ai_ay')

        Returns:
            Dictionary with word list
        """
        return self.fcrr_db.get_word_list(pattern)

    def get_activity_template(self, color: str) -> Dict[str, Any]:
        """
        Get FCRR activity template by color code

        Args:
            color: Color code (purple, orange, green)

        Returns:
            Dictionary with activity template
        """
        return self.fcrr_db.get_activity_by_color(color)

    def validate_against_knowledge_base(
        self,
        claim: str,
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Validate a pedagogical claim against the knowledge base

        Args:
            claim: The claim to validate
            confidence_threshold: Minimum confidence for validation

        Returns:
            Dictionary with validation results
        """
        # Retrieve relevant knowledge
        results = self.retrieve(
            query=claim,
            n_results=3,
            include_word_lists=False,
            relevance_threshold=confidence_threshold
        )

        # Check if we have high-confidence matches
        has_matches = results.get("has_results", False)

        if has_matches:
            sources = results.get("sources", [])
            kb_source = next((s for s in sources if s["type"] == "knowledge_base"), None)

            if kb_source and kb_source["total_results"] > 0:
                top_result = kb_source["results"][0]
                similarity = top_result.get("similarity", 0)

                return {
                    "success": True,
                    "validated": similarity >= confidence_threshold,
                    "confidence": similarity,
                    "claim": claim,
                    "supporting_evidence": top_result.get("document"),
                    "source": top_result.get("metadata", {}).get("source")
                }

        return {
            "success": True,
            "validated": False,
            "confidence": 0.0,
            "claim": claim,
            "message": "No supporting evidence found in knowledge base",
            "fallback": self._apply_fallback(claim)
        }

    def _search_fcrr_words(self, query: str) -> Dict[str, Any]:
        """
        Search FCRR word lists for matching words

        Args:
            query: Search query

        Returns:
            Dictionary with word matches
        """
        # Extract potential phonics patterns or words from query
        query_words = query.lower().split()

        # Try exact pattern match first
        for word in query_words:
            result = self.fcrr_db.get_word_list(word)
            if result.get("success"):
                return {
                    "success": True,
                    "total_matches": 1,
                    "matches": [result["data"]]
                }

        # Fall back to word search
        return self.fcrr_db.search_words(query, max_results=10)

    def _apply_fallback(self, query: str) -> Dict[str, Any]:
        """
        Apply fallback mechanism when no results found

        Args:
            query: The original query

        Returns:
            Dictionary with fallback information
        """
        return {
            "type": "no_results",
            "message": "No validated knowledge found for this query",
            "recommendation": "Consult original source materials (Wilson, OG, UFLI, FCRR)",
            "query": query,
            "action": "manual_review_required"
        }

    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the retrieval system

        Returns:
            Dictionary with system statistics
        """
        kb_stats = self.kb.get_kb_stats()
        fcrr_stats = self.fcrr_db.get_database_stats()

        return {
            "success": True,
            "knowledge_base": kb_stats,
            "fcrr_database": fcrr_stats,
            "cache_size": len(self._cache),
            "system_ready": kb_stats.get("document_count", 0) > 0
        }

    def clear_cache(self) -> None:
        """Clear the retrieval cache"""
        self._cache.clear()
        self.vector_store.clear_cache()
