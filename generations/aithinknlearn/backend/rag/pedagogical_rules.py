"""
Pedagogical Rules Retriever

Manages retrieval of pedagogical rules from WRS, OG, UFLI, and FCRR.
Provides sample rules and word lists for literacy instruction.
"""

import logging
from typing import List, Dict, Any, Optional
from backend.rag.vector_db import VectorDatabase

logger = logging.getLogger(__name__)


class PedagogicalRulesRetriever:
    """
    Retrieves and manages pedagogical rules from structured literacy frameworks
    """

    # Sample pedagogical rules from various frameworks
    SAMPLE_RULES = [
        # Wilson Reading System (WRS)
        {
            "rule_id": "wrs_001",
            "rule_text": "Closed syllable: A syllable with a single vowel followed by one or more consonants. The vowel sound is short (e.g., cat, bed, sit).",
            "source": "WRS",
            "category": "syllable_types",
            "metadata": {"syllable_type": "closed", "grade_level": "K-2"}
        },
        {
            "rule_id": "wrs_002",
            "rule_text": "Open syllable: A syllable ending in a single vowel. The vowel sound is long (e.g., me, go, she).",
            "source": "WRS",
            "category": "syllable_types",
            "metadata": {"syllable_type": "open", "grade_level": "K-2"}
        },
        {
            "rule_id": "wrs_003",
            "rule_text": "Magic E (VCe) syllable: A syllable with vowel-consonant-e pattern. The first vowel is long and e is silent (e.g., cake, made, time).",
            "source": "WRS",
            "category": "syllable_types",
            "metadata": {"syllable_type": "vce", "grade_level": "1-3"}
        },
        {
            "rule_id": "wrs_004",
            "rule_text": "Vowel team syllable: Two vowels together make one sound (e.g., rain, boat, team).",
            "source": "WRS",
            "category": "syllable_types",
            "metadata": {"syllable_type": "vowel_team", "grade_level": "2-4"}
        },

        # Orton-Gillingham (OG)
        {
            "rule_id": "og_001",
            "rule_text": "Multisensory instruction: Teach phonics using visual (seeing), auditory (hearing), kinesthetic (movement), and tactile (touch) pathways simultaneously.",
            "source": "OG",
            "category": "instruction_method",
            "metadata": {"method": "multisensory", "grade_level": "K-12"}
        },
        {
            "rule_id": "og_002",
            "rule_text": "Explicit phonics: Directly teach letter-sound correspondences in a systematic sequence, not relying on incidental learning.",
            "source": "OG",
            "category": "instruction_method",
            "metadata": {"method": "explicit", "grade_level": "K-12"}
        },
        {
            "rule_id": "og_003",
            "rule_text": "Sequential and cumulative: Introduce concepts in a logical order, building on previously learned skills.",
            "source": "OG",
            "category": "instruction_method",
            "metadata": {"method": "sequential", "grade_level": "K-12"}
        },
        {
            "rule_id": "og_004",
            "rule_text": "Short vowel sounds: a=/æ/ (cat), e=/ɛ/ (bed), i=/ɪ/ (sit), o=/ɒ/ (hot), u=/ʌ/ (cup). Always teach in closed syllables first.",
            "source": "OG",
            "category": "phonics",
            "metadata": {"skill": "short_vowels", "grade_level": "K-1"}
        },

        # UFLI Foundations
        {
            "rule_id": "ufli_001",
            "rule_text": "Decodable text: Students should read texts composed of 80%+ words containing only previously taught phonics patterns.",
            "source": "UFLI",
            "category": "decodability",
            "metadata": {"text_type": "decodable", "grade_level": "K-2"}
        },
        {
            "rule_id": "ufli_002",
            "rule_text": "CVC pattern (consonant-vowel-consonant): Foundational pattern for beginning readers. Examples: cat, dog, sun, map, bed.",
            "source": "UFLI",
            "category": "phonics",
            "metadata": {"pattern": "cvc", "grade_level": "K-1"}
        },
        {
            "rule_id": "ufli_003",
            "rule_text": "Blending practice: Students must explicitly practice blending individual phonemes into words (/c/ /a/ /t/ → cat).",
            "source": "UFLI",
            "category": "instruction_method",
            "metadata": {"skill": "blending", "grade_level": "K-1"}
        },
        {
            "rule_id": "ufli_004",
            "rule_text": "High-frequency irregular words (heart words): Teach words like 'the', 'said', 'was' explicitly, focusing on the irregular part.",
            "source": "UFLI",
            "category": "sight_words",
            "metadata": {"word_type": "irregular", "grade_level": "K-2"}
        },

        # FCRR (Florida Center for Reading Research)
        {
            "rule_id": "fcrr_001",
            "rule_text": "Phonological awareness: Ability to identify and manipulate sounds in spoken language (rhyming, syllable counting, phoneme segmentation).",
            "source": "FCRR",
            "category": "phonological_awareness",
            "metadata": {"skill": "phonological_awareness", "grade_level": "PreK-1"}
        },
        {
            "rule_id": "fcrr_002",
            "rule_text": "Phoneme segmentation: Breaking words into individual sounds (/c/ /a/ /t/). Essential skill before decoding.",
            "source": "FCRR",
            "category": "phonological_awareness",
            "metadata": {"skill": "segmentation", "grade_level": "K-1"}
        },
        {
            "rule_id": "fcrr_003",
            "rule_text": "Phoneme manipulation: Adding, deleting, or substituting phonemes (cat → mat, cat → at, cat → cap).",
            "source": "FCRR",
            "category": "phonological_awareness",
            "metadata": {"skill": "manipulation", "grade_level": "K-2"}
        },
        {
            "rule_id": "fcrr_004",
            "rule_text": "Fluency practice: Students need repeated reading practice with appropriate text to build automaticity and prosody.",
            "source": "FCRR",
            "category": "fluency",
            "metadata": {"skill": "fluency", "grade_level": "1-5"}
        },

        # Edge cases and special rules
        {
            "rule_id": "ufli_005",
            "rule_text": "Heteronyms: Words spelled the same but pronounced differently based on context (e.g., 'read' - present vs. past tense, 'tear' - rip vs. cry). Require explicit teaching with context clues.",
            "source": "UFLI",
            "category": "advanced_phonics",
            "metadata": {"skill": "heteronyms", "grade_level": "3-5"}
        },
        {
            "rule_id": "og_005",
            "rule_text": "Floss rule: After a short vowel in a one-syllable word, double f, l, or s (e.g., stuff, bell, miss). Exception: if, as, of, pal.",
            "source": "OG",
            "category": "spelling_rules",
            "metadata": {"rule_type": "floss", "grade_level": "1-3"}
        },
    ]

    # Sample word lists from FCRR database
    SAMPLE_WORD_LISTS = {
        "kindergarten_cvc": [
            "cat", "dog", "sun", "map", "bed", "pig", "top", "can", "run", "hat",
            "net", "sit", "hop", "bug", "pen", "mat", "log", "cup", "fan", "web"
        ],
        "grade1_cvce": [
            "cake", "made", "bike", "rode", "cute", "time", "home", "lake", "fine", "bone",
            "kite", "rope", "tube", "mane", "pine", "cone", "dime", "note", "make", "side"
        ],
        "grade2_vowel_teams": [
            "rain", "boat", "team", "wait", "road", "read", "goat", "paint", "teach", "mail",
            "coat", "seat", "train", "toad", "clean", "snail", "toast", "dream", "float", "steam"
        ],
        "grade3_multisyllable": [
            "sunset", "basket", "napkin", "dentist", "picnic", "cactus", "chipmunk", "hundred",
            "absent", "velvet", "goblin", "public", "serpent", "traffic", "sudden", "plastic"
        ]
    }

    def __init__(self, vector_db: Optional[VectorDatabase] = None):
        """
        Initialize pedagogical rules retriever

        Args:
            vector_db: VectorDatabase instance (creates new if not provided)
        """
        logger.info("Initializing PedagogicalRulesRetriever")

        self.vector_db = vector_db or VectorDatabase()

        # Initialize database with sample rules if empty
        if self.vector_db.count_rules() == 0:
            logger.info("Vector database empty. Initializing with sample rules.")
            self.initialize_sample_rules()
        else:
            logger.info(f"Vector database already contains {self.vector_db.count_rules()} rules")

    def initialize_sample_rules(self) -> None:
        """
        Initialize vector database with sample pedagogical rules
        """
        logger.info(f"Adding {len(self.SAMPLE_RULES)} sample rules to vector database")
        self.vector_db.add_rules_batch(self.SAMPLE_RULES)
        logger.info("Sample rules initialized successfully")

    def retrieve_rules(
        self,
        query: str,
        n_results: int = 5,
        source_filter: Optional[str] = None,
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant pedagogical rules

        Args:
            query: Query describing needed rule (e.g., "short vowel rules")
            n_results: Number of results to return
            source_filter: Filter by framework (WRS, OG, UFLI, FCRR)
            category_filter: Filter by category

        Returns:
            List of relevant rules with source citations
        """
        logger.info(f"Retrieving rules for query: '{query}'")

        results = self.vector_db.retrieve(
            query=query,
            n_results=n_results,
            source_filter=source_filter,
            category_filter=category_filter
        )

        # Add source citation to each result
        for rule in results:
            rule["citation"] = f"{rule['source']} - {rule['rule_id']}"

        logger.info(f"Retrieved {len(results)} rules")
        return results

    def get_word_list(self, grade_level: str) -> List[str]:
        """
        Retrieve grade-appropriate word list from FCRR database

        Args:
            grade_level: Grade level (kindergarten, grade1, grade2, grade3)

        Returns:
            List of words appropriate for grade level
        """
        word_list_key = None

        if grade_level.lower() in ["kindergarten", "k"]:
            word_list_key = "kindergarten_cvc"
        elif grade_level.lower() in ["grade1", "1", "first"]:
            word_list_key = "grade1_cvce"
        elif grade_level.lower() in ["grade2", "2", "second"]:
            word_list_key = "grade2_vowel_teams"
        elif grade_level.lower() in ["grade3", "3", "third"]:
            word_list_key = "grade3_multisyllable"
        else:
            word_list_key = "kindergarten_cvc"  # Default

        word_list = self.SAMPLE_WORD_LISTS.get(word_list_key, [])
        logger.info(f"Retrieved {len(word_list)} words for {grade_level}")

        return word_list

    def get_rules_by_source(self, source: str) -> List[Dict[str, Any]]:
        """
        Get all rules from a specific framework

        Args:
            source: Framework name (WRS, OG, UFLI, FCRR)

        Returns:
            List of rules from that framework
        """
        return self.retrieve_rules(
            query="all rules",
            n_results=100,
            source_filter=source
        )

    def get_rules_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all rules in a specific category

        Args:
            category: Category name

        Returns:
            List of rules in that category
        """
        return self.retrieve_rules(
            query=category,
            n_results=100,
            category_filter=category
        )
