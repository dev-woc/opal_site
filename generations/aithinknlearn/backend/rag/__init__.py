"""
RAG (Retrieval-Augmented Generation) System

Provides pedagogical grounding for literacy instruction using:
- Wilson Reading System (WRS)
- Orton-Gillingham (OG)
- UFLI Foundations
- FCRR (Florida Center for Reading Research)
"""

from backend.rag.vector_db import VectorDatabase
from backend.rag.pedagogical_rules import PedagogicalRulesRetriever
from backend.rag.constraint_validator import ConstraintValidator

__all__ = [
    "VectorDatabase",
    "PedagogicalRulesRetriever",
    "ConstraintValidator"
]
