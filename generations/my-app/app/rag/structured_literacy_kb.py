"""
Structured Literacy Knowledge Base

Ingests and manages documentation from validated literacy sources:
- Wilson Reading System
- Orton-Gillingham
- UFLI Foundations
- FCRR (Florida Center for Reading Research)
"""

from typing import List, Dict, Any, Optional
from .vector_store import VectorStore
import json


class StructuredLiteracyKB:
    """
    Knowledge base for Structured Literacy pedagogical content.

    Manages ingestion and retrieval of evidence-based literacy rules,
    phonics patterns, and teaching sequences from validated sources.
    """

    def __init__(self, vector_store: Optional[VectorStore] = None):
        """
        Initialize the knowledge base

        Args:
            vector_store: Optional VectorStore instance (creates one if not provided)
        """
        self.vector_store = vector_store or VectorStore()
        self.sources = {
            "wilson": "Wilson Reading System",
            "orton_gillingham": "Orton-Gillingham",
            "ufli": "UFLI Foundations",
            "fcrr": "Florida Center for Reading Research"
        }

    def ingest_wilson_rules(self) -> Dict[str, Any]:
        """
        Ingest Wilson Reading System rules and syllable patterns

        Returns:
            Dictionary with ingestion status
        """
        wilson_documents = [
            # Syllable Types
            {
                "content": "Wilson Syllable Type 1 - Closed Syllable: A syllable with one vowel followed by one or more consonants. The vowel sound is short. Examples: cat, sandwich, napkin, problem.",
                "metadata": {
                    "source": "wilson",
                    "category": "syllable_types",
                    "rule_name": "closed_syllable",
                    "difficulty": "beginner"
                }
            },
            {
                "content": "Wilson Syllable Type 2 - Vowel-Consonant-E (VCE): A syllable with a vowel, consonant, and silent 'e'. The first vowel is long. Examples: cake, bike, hope, mute.",
                "metadata": {
                    "source": "wilson",
                    "category": "syllable_types",
                    "rule_name": "vce_syllable",
                    "difficulty": "beginner"
                }
            },
            {
                "content": "Wilson Syllable Type 3 - Open Syllable: A syllable ending in a single vowel. The vowel sound is long. Examples: me, go, baby, student.",
                "metadata": {
                    "source": "wilson",
                    "category": "syllable_types",
                    "rule_name": "open_syllable",
                    "difficulty": "beginner"
                }
            },
            {
                "content": "Wilson Syllable Type 4 - Consonant-LE: A syllable with a consonant followed by 'le'. Found at the end of words. Examples: table, apple, little, battle.",
                "metadata": {
                    "source": "wilson",
                    "category": "syllable_types",
                    "rule_name": "consonant_le",
                    "difficulty": "intermediate"
                }
            },
            {
                "content": "Wilson Syllable Type 5 - R-Controlled: A syllable where a vowel is followed by 'r', changing the vowel sound. Examples: car, her, bird, corn, burn.",
                "metadata": {
                    "source": "wilson",
                    "category": "syllable_types",
                    "rule_name": "r_controlled",
                    "difficulty": "intermediate"
                }
            },
            {
                "content": "Wilson Syllable Type 6 - Vowel Team: A syllable with two vowels together making one sound. Examples: rain, boat, team, clue.",
                "metadata": {
                    "source": "wilson",
                    "category": "syllable_types",
                    "rule_name": "vowel_team",
                    "difficulty": "intermediate"
                }
            },
            # Orthographic Rules
            {
                "content": "Wilson 1-1-1 Doubling Rule: When a one-syllable word ends in one vowel followed by one consonant, double the final consonant before adding a vowel suffix. Examples: hop → hopping, run → running, big → bigger.",
                "metadata": {
                    "source": "wilson",
                    "category": "orthographic_rules",
                    "rule_name": "111_doubling",
                    "difficulty": "intermediate"
                }
            },
            {
                "content": "Wilson Drop E Rule: When a word ends in silent 'e', drop the 'e' before adding a vowel suffix. Examples: hope → hoping, bike → biking, take → taking.",
                "metadata": {
                    "source": "wilson",
                    "category": "orthographic_rules",
                    "rule_name": "drop_e",
                    "difficulty": "intermediate"
                }
            },
            {
                "content": "Wilson Change Y to I Rule: When a word ends in a consonant + 'y', change the 'y' to 'i' before adding a suffix (unless the suffix begins with 'i'). Examples: happy → happiness, baby → babies, funny → funnier.",
                "metadata": {
                    "source": "wilson",
                    "category": "orthographic_rules",
                    "rule_name": "y_to_i",
                    "difficulty": "intermediate"
                }
            },
            # Phonics Patterns
            {
                "content": "Wilson FLOSS Rule: Use double consonants 'ff', 'll', 'ss', or 'zz' after a single short vowel at the end of a one-syllable word. Examples: puff, hill, mess, buzz.",
                "metadata": {
                    "source": "wilson",
                    "category": "phonics_patterns",
                    "rule_name": "floss_rule",
                    "difficulty": "beginner"
                }
            }
        ]

        return self._batch_ingest(wilson_documents)

    def ingest_orton_gillingham_rules(self) -> Dict[str, Any]:
        """
        Ingest Orton-Gillingham methodology and phonics rules

        Returns:
            Dictionary with ingestion status
        """
        og_documents = [
            {
                "content": "Orton-Gillingham Multi-Sensory Approach: Instruction must engage visual (seeing), auditory (hearing), and kinesthetic-tactile (movement and touch) pathways simultaneously. Students should see, say, hear, and write each concept.",
                "metadata": {
                    "source": "orton_gillingham",
                    "category": "methodology",
                    "rule_name": "multisensory_instruction",
                    "difficulty": "foundational"
                }
            },
            {
                "content": "Orton-Gillingham Structured Sequential Learning: Instruction proceeds in a logical order from simple to complex. Each lesson builds on previously mastered concepts. No concept is introduced until prerequisite skills are secure.",
                "metadata": {
                    "source": "orton_gillingham",
                    "category": "methodology",
                    "rule_name": "sequential_learning",
                    "difficulty": "foundational"
                }
            },
            {
                "content": "Orton-Gillingham Phoneme Awareness: Students must develop the ability to hear, identify, and manipulate individual sounds (phonemes) in spoken words before learning to read. Activities include sound isolation, blending, and segmentation.",
                "metadata": {
                    "source": "orton_gillingham",
                    "category": "phonemic_awareness",
                    "rule_name": "phoneme_awareness",
                    "difficulty": "foundational"
                }
            },
            {
                "content": "Orton-Gillingham Sound-Symbol Association: Teach explicit connections between phonemes (sounds) and graphemes (letters). Each sound should have a corresponding visual symbol and kinesthetic motion.",
                "metadata": {
                    "source": "orton_gillingham",
                    "category": "phonics",
                    "rule_name": "sound_symbol_correspondence",
                    "difficulty": "foundational"
                }
            },
            {
                "content": "Orton-Gillingham Blending: Teach students to smoothly blend individual sounds together to form words. Start with continuous sounds (m, s, f) before introducing stop sounds (b, t, p). Practice both synthetic blending (sound by sound) and successive blending.",
                "metadata": {
                    "source": "orton_gillingham",
                    "category": "phonics",
                    "rule_name": "blending",
                    "difficulty": "beginner"
                }
            },
            {
                "content": "Orton-Gillingham Explicit Instruction: All concepts must be taught directly and explicitly. Do not assume students will discover patterns independently. Provide clear explanations, demonstrations, and guided practice.",
                "metadata": {
                    "source": "orton_gillingham",
                    "category": "methodology",
                    "rule_name": "explicit_instruction",
                    "difficulty": "foundational"
                }
            }
        ]

        return self._batch_ingest(og_documents)

    def ingest_ufli_foundations(self) -> Dict[str, Any]:
        """
        Ingest UFLI Foundations scope and sequence

        Returns:
            Dictionary with ingestion status
        """
        ufli_documents = [
            {
                "content": "UFLI Scope and Sequence - Unit 1: Short vowels with continuous consonants (a, i, m, s, t, f). Focus on CVC words with easily blendable sounds. Examples: sat, mat, fit, sit.",
                "metadata": {
                    "source": "ufli",
                    "category": "scope_sequence",
                    "rule_name": "unit_1_short_vowels",
                    "difficulty": "beginner",
                    "unit": 1
                }
            },
            {
                "content": "UFLI Scope and Sequence - Unit 2: Introduce stop consonants (b, d, g, p, k). Teach in combination with previously learned vowels and continuous consonants. Examples: bad, big, dog, pig, got.",
                "metadata": {
                    "source": "ufli",
                    "category": "scope_sequence",
                    "rule_name": "unit_2_stop_consonants",
                    "difficulty": "beginner",
                    "unit": 2
                }
            },
            {
                "content": "UFLI Scope and Sequence - Unit 3: Digraphs and blends (sh, ch, th, wh, bl, cl, st, etc.). Teach as single units representing one sound or sound clusters. Examples: ship, chip, this, black, stop.",
                "metadata": {
                    "source": "ufli",
                    "category": "scope_sequence",
                    "rule_name": "unit_3_digraphs_blends",
                    "difficulty": "intermediate",
                    "unit": 3
                }
            },
            {
                "content": "UFLI Decodability Standard: All reading materials must maintain at least 95% decodability based on previously taught phonics patterns. Students should never be asked to guess at words or rely on context clues for decoding.",
                "metadata": {
                    "source": "ufli",
                    "category": "methodology",
                    "rule_name": "decodability_standard",
                    "difficulty": "foundational"
                }
            },
            {
                "content": "UFLI Heart Words: High-frequency irregular words are taught as 'heart words.' Students identify the irregular part (marked with a heart), learn the regular parts through phonics, and practice the whole word. Examples: said, was, are.",
                "metadata": {
                    "source": "ufli",
                    "category": "methodology",
                    "rule_name": "heart_words",
                    "difficulty": "beginner"
                }
            }
        ]

        return self._batch_ingest(ufli_documents)

    def ingest_fcrr_guidelines(self) -> Dict[str, Any]:
        """
        Ingest FCRR activity structure and guidelines

        Returns:
            Dictionary with ingestion status
        """
        fcrr_documents = [
            {
                "content": "FCRR Purple Activities: Phonological awareness activities that develop the ability to hear and manipulate sounds in spoken words. Includes rhyming, syllable counting, onset-rime manipulation, and phoneme segmentation/blending.",
                "metadata": {
                    "source": "fcrr",
                    "category": "activity_structure",
                    "rule_name": "purple_activities",
                    "difficulty": "foundational",
                    "color_code": "purple"
                }
            },
            {
                "content": "FCRR Orange Activities: Phonics activities that teach letter-sound relationships and decoding skills. Includes sound-symbol matching, word building, blending practice, and encoding (spelling) activities.",
                "metadata": {
                    "source": "fcrr",
                    "category": "activity_structure",
                    "rule_name": "orange_activities",
                    "difficulty": "beginner",
                    "color_code": "orange"
                }
            },
            {
                "content": "FCRR Green Activities: Fluency activities that develop automatic, accurate reading with appropriate rate and expression. Includes repeated reading, partner reading, and timed reading exercises.",
                "metadata": {
                    "source": "fcrr",
                    "category": "activity_structure",
                    "rule_name": "green_activities",
                    "difficulty": "intermediate",
                    "color_code": "green"
                }
            },
            {
                "content": "FCRR Gradual Release Model: Instruction follows 'I do, We do, You do' progression. Teacher demonstrates, guides group practice, then releases to independent practice. Ensure mastery at each stage before advancing.",
                "metadata": {
                    "source": "fcrr",
                    "category": "methodology",
                    "rule_name": "gradual_release",
                    "difficulty": "foundational"
                }
            }
        ]

        return self._batch_ingest(fcrr_documents)

    def ingest_all_sources(self) -> Dict[str, Any]:
        """
        Ingest knowledge from all structured literacy sources

        Returns:
            Dictionary with comprehensive ingestion status
        """
        results = {
            "wilson": self.ingest_wilson_rules(),
            "orton_gillingham": self.ingest_orton_gillingham_rules(),
            "ufli": self.ingest_ufli_foundations(),
            "fcrr": self.ingest_fcrr_guidelines()
        }

        total_documents = sum(
            r.get("documents_added", 0) for r in results.values() if r.get("success")
        )

        stats = self.vector_store.get_collection_stats()

        return {
            "success": True,
            "sources_ingested": len([r for r in results.values() if r.get("success")]),
            "total_documents": total_documents,
            "collection_size": stats.get("document_count", 0),
            "details": results
        }

    def query_knowledge_base(
        self,
        query: str,
        source_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        Query the knowledge base for relevant rules and guidelines

        Args:
            query: The search query
            source_filter: Filter by source (wilson, orton_gillingham, ufli, fcrr)
            category_filter: Filter by category
            n_results: Number of results to return

        Returns:
            Dictionary with query results
        """
        # Build metadata filter
        where = {}
        if source_filter:
            where["source"] = source_filter
        if category_filter:
            where["category"] = category_filter

        where_clause = where if where else None

        return self.vector_store.query(
            query_text=query,
            n_results=n_results,
            where=where_clause
        )

    def get_kb_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base

        Returns:
            Dictionary with KB statistics
        """
        stats = self.vector_store.get_collection_stats()
        stats["sources"] = self.sources
        return stats

    def _batch_ingest(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Batch ingest documents into the vector store

        Args:
            documents: List of document dictionaries with 'content' and 'metadata'

        Returns:
            Dictionary with ingestion status
        """
        if not documents:
            return {"success": False, "error": "No documents provided"}

        contents = [doc["content"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]

        return self.vector_store.add_documents(
            documents=contents,
            metadatas=metadatas
        )
