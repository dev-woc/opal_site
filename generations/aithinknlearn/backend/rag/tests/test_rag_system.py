"""
Comprehensive RAG System Test Suite

Tests all 7 required test steps:
1. Vector database setup with embedded rules
2. RAG retrieval for grapheme patterns
3. Word list retrieval from FCRR database
4. GPT-4o constraint validation
5. Non-compliant suggestion rejection
6. Heteronym edge case handling
7. Source citation verification
"""

import pytest
import logging
from backend.rag import VectorDatabase, PedagogicalRulesRetriever, ConstraintValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestVectorDatabase:
    """Test 1: Vector database setup with embedded rules"""

    def test_vector_db_initialization(self):
        """Test vector database initialization"""
        logger.info("TEST 1: Testing vector database initialization")

        vector_db = VectorDatabase(persist_directory="./test_chroma_db")
        assert vector_db is not None
        assert vector_db.collection is not None

        logger.info("TEST 1 PASSED: Vector database initialized")

    def test_add_and_retrieve_rule(self):
        """Test adding and retrieving a single rule"""
        logger.info("TEST 1: Testing rule storage and retrieval")

        vector_db = VectorDatabase(persist_directory="./test_chroma_db")

        # Add a test rule
        vector_db.add_rule(
            rule_id="test_001",
            rule_text="Short vowel /a/ in closed syllable: cat, hat, mat",
            source="TEST",
            category="phonics"
        )

        # Retrieve the rule
        rule = vector_db.get_rule_by_id("test_001")
        assert rule is not None
        assert "cat" in rule["rule_text"]

        logger.info("TEST 1 PASSED: Rule storage and retrieval works")

    def test_batch_rule_addition(self):
        """Test batch rule addition"""
        logger.info("TEST 1: Testing batch rule addition")

        vector_db = VectorDatabase(persist_directory="./test_chroma_db")

        rules = [
            {
                "rule_id": "batch_001",
                "rule_text": "Closed syllable rule",
                "source": "WRS",
                "category": "syllable_types"
            },
            {
                "rule_id": "batch_002",
                "rule_text": "Open syllable rule",
                "source": "WRS",
                "category": "syllable_types"
            }
        ]

        vector_db.add_rules_batch(rules)
        count = vector_db.count_rules()
        assert count >= 2

        logger.info(f"TEST 1 PASSED: Batch addition works ({count} rules in DB)")

    def test_semantic_search(self):
        """Test semantic search retrieval"""
        logger.info("TEST 1: Testing semantic search")

        vector_db = VectorDatabase(persist_directory="./test_chroma_db")

        # Add rules with semantic content
        vector_db.add_rule(
            rule_id="semantic_001",
            rule_text="Short vowels in CVC words: cat, dog, sun",
            source="TEST",
            category="phonics"
        )

        # Search with semantic query
        results = vector_db.retrieve(query="short vowel sounds", n_results=3)
        assert len(results) > 0

        logger.info(f"TEST 1 PASSED: Semantic search returned {len(results)} results")


class TestPedagogicalRulesRetriever:
    """Test 2 & 3: RAG retrieval for grapheme patterns and word lists"""

    def test_initialize_sample_rules(self):
        """Test 2: Initialize retriever with sample rules"""
        logger.info("TEST 2: Testing sample rules initialization")

        retriever = PedagogicalRulesRetriever()
        count = retriever.vector_db.count_rules()

        assert count > 0
        logger.info(f"TEST 2 PASSED: Initialized with {count} sample rules")

    def test_retrieve_phonetic_rules(self):
        """Test 2: Retrieve rules for specific grapheme patterns"""
        logger.info("TEST 2: Testing grapheme pattern retrieval")

        retriever = PedagogicalRulesRetriever()

        # Test short vowel retrieval
        rules = retriever.retrieve_rules(
            query="short vowel sounds in closed syllables",
            n_results=5
        )

        assert len(rules) > 0
        assert any("short" in r["rule_text"].lower() for r in rules)

        # Check source citations
        for rule in rules:
            assert "citation" in rule
            assert rule["source"] in rule["citation"]

        logger.info(f"TEST 2 PASSED: Retrieved {len(rules)} phonetic rules with citations")

    def test_retrieve_syllable_type_rules(self):
        """Test 2: Retrieve syllable type rules"""
        logger.info("TEST 2: Testing syllable type rule retrieval")

        retriever = PedagogicalRulesRetriever()

        rules = retriever.retrieve_rules(
            query="syllable types",
            category_filter="syllable_types",
            n_results=5
        )

        assert len(rules) > 0
        logger.info(f"TEST 2 PASSED: Retrieved {len(rules)} syllable type rules")

    def test_filter_by_source(self):
        """Test 2: Filter rules by framework source"""
        logger.info("TEST 2: Testing source filtering")

        retriever = PedagogicalRulesRetriever()

        # Test WRS filtering
        wrs_rules = retriever.retrieve_rules(
            query="phonics",
            source_filter="WRS",
            n_results=10
        )

        for rule in wrs_rules:
            assert rule["source"] == "WRS"

        logger.info(f"TEST 2 PASSED: Retrieved {len(wrs_rules)} WRS rules")

    def test_word_list_retrieval(self):
        """Test 3: Retrieve word lists from FCRR database"""
        logger.info("TEST 3: Testing word list retrieval")

        retriever = PedagogicalRulesRetriever()

        # Test kindergarten word list
        k_words = retriever.get_word_list("kindergarten")
        assert len(k_words) > 0
        assert "cat" in k_words
        assert "dog" in k_words

        # Test grade 1 word list
        g1_words = retriever.get_word_list("grade1")
        assert len(g1_words) > 0
        assert any("cake" in w or "make" in w for w in g1_words)

        logger.info(f"TEST 3 PASSED: Retrieved K={len(k_words)} and G1={len(g1_words)} words")

    def test_grade_appropriate_vocabulary(self):
        """Test 3: Verify grade-appropriate vocabulary"""
        logger.info("TEST 3: Testing grade-appropriate word lists")

        retriever = PedagogicalRulesRetriever()

        # Kindergarten should have simple CVC words
        k_words = retriever.get_word_list("kindergarten")
        assert all(len(w) <= 4 for w in k_words[:10])  # Simple short words

        # Grade 2 should have vowel teams
        g2_words = retriever.get_word_list("grade2")
        vowel_teams = ["ai", "oa", "ea", "ee"]
        has_vowel_teams = any(
            any(team in word for team in vowel_teams)
            for word in g2_words
        )
        assert has_vowel_teams

        logger.info("TEST 3 PASSED: Word lists are grade-appropriate")


class TestConstraintValidator:
    """Test 4 & 5: GPT-4o constraint validation and rejection"""

    def test_decodability_validation_pass(self):
        """Test 4: Validate compliant decodable text"""
        logger.info("TEST 4: Testing decodability validation (pass case)")

        validator = ConstraintValidator()

        text = "The cat sat on the mat."
        allowed_phonemes = ["cvc", "short_vowels"]
        allowed_sight_words = ["the", "on"]

        result = validator.validate_decodability(
            text=text,
            allowed_phonemes=allowed_phonemes,
            allowed_sight_words=allowed_sight_words
        )

        assert result["is_valid"] == True
        assert result["compliance_rate"] >= 0.80

        logger.info(f"TEST 4 PASSED: Compliant text validated ({result['compliance_rate']*100:.1f}% compliant)")

    def test_decodability_validation_fail(self):
        """Test 5: Reject non-compliant text"""
        logger.info("TEST 5: Testing non-compliant text rejection")

        validator = ConstraintValidator()

        # Text with complex words not in allowed phonemes
        text = "The extraordinary phenomenon perplexed scientists."
        allowed_phonemes = ["cvc", "short_vowels"]
        allowed_sight_words = ["the"]

        result = validator.validate_decodability(
            text=text,
            allowed_phonemes=allowed_phonemes,
            allowed_sight_words=allowed_sight_words
        )

        assert result["is_valid"] == False
        assert len(result["violations"]) > 0

        logger.info(f"TEST 5 PASSED: Non-compliant text rejected ({len(result['violations'])} violations)")

    def test_constraint_validation(self):
        """Test 4: Comprehensive constraint validation"""
        logger.info("TEST 4: Testing comprehensive constraint validation")

        validator = ConstraintValidator()
        retriever = PedagogicalRulesRetriever()

        # Get some pedagogical rules
        rules = retriever.retrieve_rules(query="decodable text requirements", n_results=3)

        # Validate compliant output
        compliant_text = "The cat sat on the mat and ran to the den."
        constraints = {
            "allowed_phonemes": ["cvc", "short_vowels"],
            "retrieved_rules": rules,
            "allowed_sight_words": ["the", "to", "and", "on"]
        }

        result = validator.validate_output(compliant_text, constraints)
        assert "validations" in result
        assert "decodability" in result["validations"]

        logger.info(f"TEST 4 PASSED: Comprehensive validation completed")

    def test_rejection_system(self):
        """Test 5: Test rejection system for non-compliant outputs"""
        logger.info("TEST 5: Testing rejection system")

        validator = ConstraintValidator()
        retriever = PedagogicalRulesRetriever()

        rules = retriever.retrieve_rules(query="decodable text", n_results=2)

        # Non-compliant output
        non_compliant_text = "The extraordinary phenomenon was incredibly perplexing."
        constraints = {
            "allowed_phonemes": ["cvc"],
            "retrieved_rules": rules,
            "allowed_sight_words": ["the", "was"]
        }

        rejection = validator.reject_non_compliant(non_compliant_text, constraints)

        assert rejection["accepted"] == False
        assert rejection["rejection_reason"] is not None

        logger.info(f"TEST 5 PASSED: Non-compliant output rejected - {rejection['rejection_reason']}")


class TestEdgeCases:
    """Test 6: Edge cases including heteronyms"""

    def test_heteronym_handling(self):
        """Test 6: Handle heteronyms with proper UFLI context"""
        logger.info("TEST 6: Testing heteronym edge case handling")

        retriever = PedagogicalRulesRetriever()

        # Retrieve heteronym rule
        rules = retriever.retrieve_rules(
            query="heteronyms words with different pronunciations",
            source_filter="UFLI",
            n_results=5
        )

        # Should find the heteronym rule
        heteronym_rule = None
        for rule in rules:
            if "heteronym" in rule["rule_text"].lower():
                heteronym_rule = rule
                break

        assert heteronym_rule is not None
        assert "context" in heteronym_rule["rule_text"].lower()

        logger.info(f"TEST 6 PASSED: Heteronym rule found - {heteronym_rule['rule_id']}")

    def test_rule_conflict_resolution(self):
        """Test 6: Handle conflicting rules"""
        logger.info("TEST 6: Testing rule conflict edge case")

        retriever = PedagogicalRulesRetriever()

        # Get rules from different frameworks
        wrs_rules = retriever.retrieve_rules(query="syllable", source_filter="WRS", n_results=3)
        og_rules = retriever.retrieve_rules(query="syllable", source_filter="OG", n_results=3)

        # Both should return results
        assert len(wrs_rules) > 0
        assert len(og_rules) > 0

        logger.info(f"TEST 6 PASSED: Retrieved rules from multiple frameworks (WRS={len(wrs_rules)}, OG={len(og_rules)})")

    def test_empty_query_handling(self):
        """Test 6: Handle edge case of empty query"""
        logger.info("TEST 6: Testing empty query edge case")

        retriever = PedagogicalRulesRetriever()

        # Empty query should still return results (fallback behavior)
        rules = retriever.retrieve_rules(query="", n_results=3)

        # Should handle gracefully
        assert isinstance(rules, list)

        logger.info(f"TEST 6 PASSED: Empty query handled gracefully")


class TestSourceCitations:
    """Test 7: Source citation verification"""

    def test_citation_format(self):
        """Test 7: Verify all retrieved rules include source citations"""
        logger.info("TEST 7: Testing source citation format")

        retriever = PedagogicalRulesRetriever()

        rules = retriever.retrieve_rules(query="phonics instruction", n_results=5)

        for rule in rules:
            # Check citation exists
            assert "citation" in rule
            assert rule["citation"] is not None

            # Check citation format: "SOURCE - rule_id"
            assert "-" in rule["citation"]
            assert rule["source"] in rule["citation"]
            assert rule["rule_id"] in rule["citation"]

        logger.info(f"TEST 7 PASSED: All {len(rules)} rules have proper citations")

    def test_teacher_accountability_metadata(self):
        """Test 7: Verify metadata for teacher accountability"""
        logger.info("TEST 7: Testing teacher accountability metadata")

        retriever = PedagogicalRulesRetriever()

        rules = retriever.retrieve_rules(query="instruction", n_results=5)

        for rule in rules:
            # Should have source
            assert "source" in rule
            assert rule["source"] in ["WRS", "OG", "UFLI", "FCRR"]

            # Should have category
            assert "category" in rule

            # Should have metadata
            assert "metadata" in rule

            # Metadata should have grade_level for teacher planning
            metadata = rule["metadata"]
            if "grade_level" in metadata:
                assert metadata["grade_level"] is not None

        logger.info(f"TEST 7 PASSED: All rules contain teacher accountability metadata")

    def test_citation_tracking(self):
        """Test 7: Verify citation tracking through full pipeline"""
        logger.info("TEST 7: Testing citation tracking through pipeline")

        retriever = PedagogicalRulesRetriever()
        validator = ConstraintValidator()

        # Retrieve rules
        rules = retriever.retrieve_rules(query="decodable text", n_results=3)

        # Verify each rule has citation
        for rule in rules:
            assert "citation" in rule

        # Use rules in validation
        constraints = {
            "allowed_phonemes": ["cvc"],
            "retrieved_rules": rules
        }

        text = "The cat sat."
        result = validator.validate_output(text, constraints)

        # Validation should complete with cited rules
        assert result is not None

        logger.info(f"TEST 7 PASSED: Citations tracked through full pipeline")


# Integration test
def test_full_rag_integration():
    """Integration test: Full RAG pipeline"""
    logger.info("INTEGRATION TEST: Testing full RAG pipeline")

    # 1. Initialize components
    retriever = PedagogicalRulesRetriever()
    validator = ConstraintValidator()

    # 2. Retrieve rules for specific teaching scenario
    rules = retriever.retrieve_rules(
        query="teaching short vowels in CVC words",
        n_results=5
    )
    assert len(rules) > 0

    # 3. Get appropriate word list
    word_list = retriever.get_word_list("kindergarten")
    assert len(word_list) > 0

    # 4. Validate a decodable sentence
    test_sentence = "The cat sat on a mat."
    constraints = {
        "allowed_phonemes": ["cvc", "short_vowels"],
        "retrieved_rules": rules,
        "allowed_sight_words": ["the", "a", "on"]
    }

    validation = validator.validate_output(test_sentence, constraints)
    assert validation is not None

    # 5. Check rejection system
    rejection = validator.reject_non_compliant(test_sentence, constraints)
    assert "accepted" in rejection

    logger.info(f"INTEGRATION TEST PASSED: Full RAG pipeline works end-to-end")


if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v", "-s"])
