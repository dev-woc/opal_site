"""
Comprehensive RAG System Test Suite

Tests all aspects of the RAG-powered pedagogical grounding system:
- Vector store operations
- Knowledge base ingestion and retrieval
- FCRR database word lists
- Retrieval engine with relevance scoring
- Caching mechanisms
- Fallback handling
"""

import sys
import os

# Add app to path
sys.path.insert(0, os.path.abspath('.'))

from app.rag import VectorStore, StructuredLiteracyKB, FCRRDatabase, RetrievalEngine
import time


class RAGSystemTest:
    """Comprehensive test suite for RAG system"""

    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0

    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "PASS"
        else:
            status = "FAIL"

        result = f"[{status}] {test_name}"
        if details:
            result += f"\n      {details}"

        self.test_results.append(result)
        print(result)

    def test_vector_store_initialization(self) -> bool:
        """Test 1: Vector store initialization"""
        print("\n=== Test 1: Vector Store Initialization ===")
        try:
            vector_store = VectorStore(collection_name="test_collection")
            stats = vector_store.get_collection_stats()

            passed = stats.get("success", False)
            details = f"Collection: {stats.get('collection_name')}, Docs: {stats.get('document_count', 0)}"
            self.log_test("Vector Store Initialization", passed, details)
            return passed
        except Exception as e:
            self.log_test("Vector Store Initialization", False, f"Error: {str(e)}")
            return False

    def test_vector_store_add_query(self) -> bool:
        """Test 2: Vector store add and query documents"""
        print("\n=== Test 2: Vector Store Add/Query ===")
        try:
            vector_store = VectorStore(collection_name="test_add_query")

            # Add documents
            docs = [
                "The closed syllable has a short vowel sound.",
                "Open syllables end with a long vowel sound.",
                "R-controlled vowels change the sound of the vowel."
            ]
            metadatas = [
                {"type": "syllable", "category": "closed"},
                {"type": "syllable", "category": "open"},
                {"type": "syllable", "category": "r_controlled"}
            ]

            add_result = vector_store.add_documents(documents=docs, metadatas=metadatas)

            if not add_result.get("success"):
                self.log_test("Add Documents", False, f"Error: {add_result.get('error')}")
                return False

            # Query documents
            query_result = vector_store.query("short vowel", n_results=2)

            passed = (query_result.get("success") and
                     query_result.get("total_results", 0) > 0)

            details = f"Added {add_result.get('documents_added')} docs, Retrieved {query_result.get('total_results')} results"
            self.log_test("Vector Store Add/Query", passed, details)
            return passed

        except Exception as e:
            self.log_test("Vector Store Add/Query", False, f"Error: {str(e)}")
            return False

    def test_structured_literacy_kb_ingestion(self) -> bool:
        """Test 3: Structured Literacy KB ingestion"""
        print("\n=== Test 3: Structured Literacy KB Ingestion ===")
        try:
            kb = StructuredLiteracyKB()

            # Ingest all sources
            result = kb.ingest_all_sources()

            passed = (result.get("success") and
                     result.get("total_documents", 0) > 0)

            details = (f"Sources: {result.get('sources_ingested')}, "
                      f"Total Docs: {result.get('total_documents')}, "
                      f"Collection Size: {result.get('collection_size')}")

            self.log_test("KB Ingestion", passed, details)
            return passed

        except Exception as e:
            self.log_test("KB Ingestion", False, f"Error: {str(e)}")
            return False

    def test_kb_query_phonics_rules(self) -> bool:
        """Test 4: Query KB for specific phonics rules"""
        print("\n=== Test 4: Query Phonics Rules ===")
        try:
            kb = StructuredLiteracyKB()
            kb.ingest_all_sources()

            # Query for syllable types
            result = kb.query_knowledge_base("closed syllable short vowel", n_results=3)

            passed = (result.get("success") and
                     result.get("total_results", 0) > 0)

            details = f"Query: 'closed syllable', Results: {result.get('total_results')}"
            if passed and result.get("results"):
                top_result = result["results"][0]
                details += f"\n      Top match: {top_result['document'][:100]}..."
                details += f"\n      Similarity: {top_result['similarity']:.3f}"

            self.log_test("Query Phonics Rules", passed, details)
            return passed

        except Exception as e:
            self.log_test("Query Phonics Rules", False, f"Error: {str(e)}")
            return False

    def test_kb_source_filtering(self) -> bool:
        """Test 5: Query KB with source filtering"""
        print("\n=== Test 5: KB Source Filtering ===")
        try:
            kb = StructuredLiteracyKB()
            kb.ingest_all_sources()

            # Query Wilson-specific content
            wilson_result = kb.query_knowledge_base(
                "syllable types",
                source_filter="wilson",
                n_results=3
            )

            # Query OG-specific content
            og_result = kb.query_knowledge_base(
                "multisensory instruction",
                source_filter="orton_gillingham",
                n_results=3
            )

            passed = (wilson_result.get("success") and
                     og_result.get("success") and
                     wilson_result.get("total_results", 0) > 0 and
                     og_result.get("total_results", 0) > 0)

            details = (f"Wilson results: {wilson_result.get('total_results')}, "
                      f"OG results: {og_result.get('total_results')}")

            self.log_test("Source Filtering", passed, details)
            return passed

        except Exception as e:
            self.log_test("Source Filtering", False, f"Error: {str(e)}")
            return False

    def test_fcrr_word_lists(self) -> bool:
        """Test 6: FCRR word list retrieval"""
        print("\n=== Test 6: FCRR Word Lists ===")
        try:
            fcrr_db = FCRRDatabase()

            # Get CVC word list
            cvc_result = fcrr_db.get_word_list("cvc_a")

            # Get digraph word list
            digraph_result = fcrr_db.get_word_list("sh")

            passed = (cvc_result.get("success") and
                     digraph_result.get("success") and
                     len(cvc_result.get("data", {}).get("words", [])) > 0)

            details = (f"CVC 'a' words: {len(cvc_result.get('data', {}).get('words', []))}, "
                      f"'sh' words: {len(digraph_result.get('data', {}).get('words', []))}")

            self.log_test("FCRR Word Lists", passed, details)
            return passed

        except Exception as e:
            self.log_test("FCRR Word Lists", False, f"Error: {str(e)}")
            return False

    def test_fcrr_activities(self) -> bool:
        """Test 7: FCRR activity templates"""
        print("\n=== Test 7: FCRR Activity Templates ===")
        try:
            fcrr_db = FCRRDatabase()

            # Get activities by color
            purple = fcrr_db.get_activity_by_color("purple")
            orange = fcrr_db.get_activity_by_color("orange")
            green = fcrr_db.get_activity_by_color("green")

            passed = (purple.get("success") and
                     orange.get("success") and
                     green.get("success"))

            details = (f"Purple activities: {len(purple.get('data', {}).get('activities', []))}, "
                      f"Orange: {len(orange.get('data', {}).get('activities', []))}, "
                      f"Green: {len(green.get('data', {}).get('activities', []))}")

            self.log_test("FCRR Activities", passed, details)
            return passed

        except Exception as e:
            self.log_test("FCRR Activities", False, f"Error: {str(e)}")
            return False

    def test_retrieval_engine_initialization(self) -> bool:
        """Test 8: Retrieval engine initialization"""
        print("\n=== Test 8: Retrieval Engine Init ===")
        try:
            engine = RetrievalEngine(auto_initialize_kb=True)
            stats = engine.get_system_stats()

            passed = (stats.get("success") and
                     stats.get("system_ready", False))

            details = (f"KB Docs: {stats.get('knowledge_base', {}).get('document_count')}, "
                      f"FCRR Words: {stats.get('fcrr_database', {}).get('total_words')}")

            self.log_test("Retrieval Engine Init", passed, details)
            return passed

        except Exception as e:
            self.log_test("Retrieval Engine Init", False, f"Error: {str(e)}")
            return False

    def test_retrieval_engine_query(self) -> bool:
        """Test 9: Retrieval engine query with multi-source results"""
        print("\n=== Test 9: Retrieval Engine Query ===")
        try:
            engine = RetrievalEngine(auto_initialize_kb=True)

            # Query for phonics rules
            result = engine.retrieve(
                query="doubling rule consonant",
                n_results=5,
                include_word_lists=True
            )

            passed = (result.get("success") and
                     result.get("has_results", False))

            details = (f"Sources: {result.get('total_sources')}, "
                      f"Has Results: {result.get('has_results')}, "
                      f"Time: {result.get('retrieval_time_ms')}ms")

            self.log_test("Retrieval Engine Query", passed, details)
            return passed

        except Exception as e:
            self.log_test("Retrieval Engine Query", False, f"Error: {str(e)}")
            return False

    def test_retrieval_caching(self) -> bool:
        """Test 10: Retrieval caching mechanism"""
        print("\n=== Test 10: Retrieval Caching ===")
        try:
            engine = RetrievalEngine(auto_initialize_kb=True)

            # First query (not cached)
            start1 = time.time()
            result1 = engine.retrieve("syllable types", n_results=3)
            time1 = (time.time() - start1) * 1000

            # Second query (should be cached)
            start2 = time.time()
            result2 = engine.retrieve("syllable types", n_results=3)
            time2 = (time.time() - start2) * 1000

            passed = (result1.get("success") and
                     result2.get("success") and
                     result2.get("cached", False))

            details = (f"First query: {time1:.2f}ms, "
                      f"Cached query: {time2:.2f}ms, "
                      f"Speedup: {time1/time2 if time2 > 0 else 0:.1f}x")

            self.log_test("Retrieval Caching", passed, details)
            return passed

        except Exception as e:
            self.log_test("Retrieval Caching", False, f"Error: {str(e)}")
            return False

    def test_retrieval_for_lesson_planning(self) -> bool:
        """Test 11: Retrieval for lesson planning"""
        print("\n=== Test 11: Retrieval for Lesson Planning ===")
        try:
            engine = RetrievalEngine(auto_initialize_kb=True)

            result = engine.retrieve_for_lesson_planning(
                learning_objective="teaching short vowel CVC words",
                difficulty="beginner"
            )

            passed = (result.get("success") and
                     "resources" in result and
                     "word_lists" in result["resources"])

            details = f"Resources: {len(result.get('resources', {}))}"
            self.log_test("Lesson Planning Retrieval", passed, details)
            return passed

        except Exception as e:
            self.log_test("Lesson Planning Retrieval", False, f"Error: {str(e)}")
            return False

    def test_validation_against_kb(self) -> bool:
        """Test 12: Validate claims against knowledge base"""
        print("\n=== Test 12: Knowledge Base Validation ===")
        try:
            engine = RetrievalEngine(auto_initialize_kb=True)

            # Valid claim
            valid_claim = "closed syllables have short vowel sounds"
            valid_result = engine.validate_against_knowledge_base(valid_claim)

            # Invalid/unknown claim
            invalid_claim = "use three-cueing system for reading"
            invalid_result = engine.validate_against_knowledge_base(invalid_claim)

            passed = (valid_result.get("success") and
                     valid_result.get("validated", False))

            details = (f"Valid claim validated: {valid_result.get('validated')}, "
                      f"Confidence: {valid_result.get('confidence', 0):.3f}")

            self.log_test("KB Validation", passed, details)
            return passed

        except Exception as e:
            self.log_test("KB Validation", False, f"Error: {str(e)}")
            return False

    def test_edge_case_retrieval(self) -> bool:
        """Test 13: Edge case handling"""
        print("\n=== Test 13: Edge Case Handling ===")
        try:
            engine = RetrievalEngine(auto_initialize_kb=True)

            # Empty query
            empty_result = engine.retrieve("", n_results=5)

            # Very specific query
            specific_result = engine.retrieve(
                "Wilson 1-1-1 doubling rule consonant suffix",
                n_results=5
            )

            # Query with no matches (should trigger fallback)
            no_match_result = engine.retrieve(
                "quantum physics string theory",
                n_results=5
            )

            passed = (empty_result.get("success") and
                     specific_result.get("success") and
                     no_match_result.get("success"))

            has_fallback = "fallback" in no_match_result

            details = f"Specific query results: {specific_result.get('has_results')}, Fallback triggered: {has_fallback}"
            self.log_test("Edge Case Handling", passed, details)
            return passed

        except Exception as e:
            self.log_test("Edge Case Handling", False, f"Error: {str(e)}")
            return False

    def test_performance_benchmark(self) -> bool:
        """Test 14: Performance benchmarking"""
        print("\n=== Test 14: Performance Benchmark ===")
        try:
            engine = RetrievalEngine(auto_initialize_kb=True)

            queries = [
                "phoneme blending",
                "multisensory instruction",
                "decodability rate",
                "r-controlled vowels",
                "syllable division"
            ]

            total_time = 0
            results_count = 0

            for query in queries:
                start = time.time()
                result = engine.retrieve(query, n_results=3)
                query_time = (time.time() - start) * 1000

                total_time += query_time
                if result.get("has_results"):
                    results_count += 1

            avg_time = total_time / len(queries)
            passed = avg_time < 1000  # Average should be under 1 second

            details = (f"Avg query time: {avg_time:.2f}ms, "
                      f"Queries with results: {results_count}/{len(queries)}")

            self.log_test("Performance Benchmark", passed, details)
            return passed

        except Exception as e:
            self.log_test("Performance Benchmark", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all tests and generate report"""
        print("\n" + "=" * 70)
        print("RAG SYSTEM COMPREHENSIVE TEST SUITE")
        print("=" * 70)

        # Run all tests
        self.test_vector_store_initialization()
        self.test_vector_store_add_query()
        self.test_structured_literacy_kb_ingestion()
        self.test_kb_query_phonics_rules()
        self.test_kb_source_filtering()
        self.test_fcrr_word_lists()
        self.test_fcrr_activities()
        self.test_retrieval_engine_initialization()
        self.test_retrieval_engine_query()
        self.test_retrieval_caching()
        self.test_retrieval_for_lesson_planning()
        self.test_validation_against_kb()
        self.test_edge_case_retrieval()
        self.test_performance_benchmark()

        # Print summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {(self.passed_tests / self.total_tests * 100):.1f}%")
        print("=" * 70)

        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.total_tests - self.passed_tests,
            "success_rate": self.passed_tests / self.total_tests * 100,
            "all_passed": self.passed_tests == self.total_tests
        }


if __name__ == "__main__":
    print("Starting RAG System Test Suite...")
    print("This will test all components of the RAG-powered pedagogical grounding system.\n")

    tester = RAGSystemTest()
    results = tester.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if results["all_passed"] else 1)
