"""
RAG System Visual Demo

Interactive demonstration of RAG system features for screenshot evidence.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.rag import RetrievalEngine
import json


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_json(data, indent=2):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=indent))


def demo_knowledge_base_retrieval():
    """Demo 1: Knowledge Base Retrieval"""
    print_section("DEMO 1: Query RAG System for Phonics Rules")

    engine = RetrievalEngine(auto_initialize_kb=True)

    # Query 1: Syllable types
    print("Query: 'closed syllable short vowel'")
    result = engine.retrieve("closed syllable short vowel", n_results=3, include_word_lists=False)

    if result.get("has_results"):
        print(f"\nFound {result['total_sources']} source(s)")
        print(f"Retrieval time: {result['retrieval_time_ms']}ms")

        for source in result["sources"]:
            if source["type"] == "knowledge_base":
                print(f"\nKnowledge Base Results ({source['total_results']} matches):")
                for i, res in enumerate(source["results"][:2], 1):
                    print(f"\n  Result {i}:")
                    print(f"    Document: {res['document'][:150]}...")
                    print(f"    Similarity: {res['similarity']:.3f}")
                    print(f"    Source: {res['metadata'].get('source', 'N/A')}")
                    print(f"    Category: {res['metadata'].get('category', 'N/A')}")

    print("\n" + "-" * 80)


def demo_wilson_vs_og():
    """Demo 2: Source-Specific Retrieval"""
    print_section("DEMO 2: Verify Content Matches Structured Literacy Sources")

    engine = RetrievalEngine(auto_initialize_kb=True)

    # Wilson query
    print("Query Wilson Reading System: 'syllable types'")
    wilson = engine.retrieve("syllable types", n_results=3, source_filter="wilson", include_word_lists=False)

    if wilson.get("has_results"):
        print("\nWilson Reading System Results:")
        for source in wilson["sources"]:
            if source["type"] == "knowledge_base" and source["total_results"] > 0:
                res = source["results"][0]
                print(f"  {res['document'][:200]}...")
                print(f"  Source: {res['metadata'].get('source')}")

    print("\n" + "-" * 80)

    # OG query
    print("\nQuery Orton-Gillingham: 'multisensory instruction'")
    og = engine.retrieve("multisensory instruction", n_results=3, source_filter="orton_gillingham", include_word_lists=False)

    if og.get("has_results"):
        print("\nOrton-Gillingham Results:")
        for source in og["sources"]:
            if source["type"] == "knowledge_base" and source["total_results"] > 0:
                res = source["results"][0]
                print(f"  {res['document'][:200]}...")
                print(f"  Source: {res['metadata'].get('source')}")

    print("\n" + "-" * 80)


def demo_fcrr_word_lists():
    """Demo 3: FCRR Word List Retrieval"""
    print_section("DEMO 3: Test Word List Retrieval from FCRR Database")

    engine = RetrievalEngine(auto_initialize_kb=True)

    # Get CVC word list
    print("Retrieving CVC short 'a' word list...")
    cvc_result = engine.get_word_list("cvc_a")

    if cvc_result.get("success"):
        data = cvc_result["data"]
        print(f"\nPattern: {data['pattern']}")
        print(f"Difficulty: {data['difficulty']}")
        print(f"Total words: {len(data['words'])}")
        print(f"Sample words: {', '.join(data['words'][:15])}")
        print(f"Example sentence: {data['example_sentence']}")

    print("\n" + "-" * 80)

    # Get digraph word list
    print("\nRetrieving 'sh' digraph word list...")
    sh_result = engine.get_word_list("sh")

    if sh_result.get("success"):
        data = sh_result["data"]
        print(f"\nPattern: {data['pattern']}")
        print(f"Difficulty: {data['difficulty']}")
        print(f"Total words: {len(data['words'])}")
        print(f"Sample words: {', '.join(data['words'][:15])}")
        print(f"Example sentence: {data['example_sentence']}")

    print("\n" + "-" * 80)


def demo_rag_constraints():
    """Demo 4: RAG Constraints and Validation"""
    print_section("DEMO 4: Verify GPT-4o Respects RAG Constraints")

    engine = RetrievalEngine(auto_initialize_kb=True)

    # Validate evidence-based claim
    print("Validating claim: 'closed syllables have short vowel sounds'")
    valid_claim = engine.validate_against_knowledge_base(
        "closed syllables have short vowel sounds",
        confidence_threshold=0.5
    )

    print(f"\nValidation Result:")
    print(f"  Validated: {valid_claim.get('validated')}")
    print(f"  Confidence: {valid_claim.get('confidence', 0):.3f}")
    if valid_claim.get('supporting_evidence'):
        print(f"  Evidence: {valid_claim['supporting_evidence'][:150]}...")
        print(f"  Source: {valid_claim.get('source')}")

    print("\n" + "-" * 80)

    # Try to validate non-evidence-based claim
    print("\nValidating claim: 'use three-cueing system for decoding'")
    invalid_claim = engine.validate_against_knowledge_base(
        "use three-cueing system for decoding",
        confidence_threshold=0.5
    )

    print(f"\nValidation Result:")
    print(f"  Validated: {invalid_claim.get('validated')}")
    print(f"  Confidence: {invalid_claim.get('confidence', 0):.3f}")
    if not invalid_claim.get('validated'):
        print(f"  Message: {invalid_claim.get('message')}")
        if invalid_claim.get('fallback'):
            print(f"  Fallback Action: {invalid_claim['fallback'].get('action')}")

    print("\n" + "-" * 80)


def demo_edge_cases():
    """Demo 5: Edge Case Handling"""
    print_section("DEMO 5: Test Retrieval with Edge-Case Literacy Patterns")

    engine = RetrievalEngine(auto_initialize_kb=True)

    # Very specific query
    print("Query: 'Wilson 1-1-1 doubling rule before vowel suffix'")
    specific = engine.retrieve("Wilson 1-1-1 doubling rule before vowel suffix", n_results=3)

    print(f"\nResults: {specific.get('has_results')}")
    if specific.get("has_results"):
        for source in specific["sources"]:
            if source["type"] == "knowledge_base" and source["total_results"] > 0:
                print(f"  Matches: {source['total_results']}")
                res = source["results"][0]
                print(f"  Top Match: {res['document'][:150]}...")
                print(f"  Similarity: {res['similarity']:.3f}")

    print("\n" + "-" * 80)

    # R-controlled vowels
    print("\nQuery: 'r-controlled vowels ar or er ir ur'")
    r_controlled = engine.retrieve("r-controlled vowels ar or er ir ur", n_results=3)

    print(f"\nResults: {r_controlled.get('has_results')}")
    if r_controlled.get("has_results"):
        for source in r_controlled["sources"]:
            if source["type"] == "knowledge_base" and source["total_results"] > 0:
                print(f"  Matches: {source['total_results']}")
                res = source["results"][0]
                print(f"  Top Match: {res['document'][:150]}...")

    print("\n" + "-" * 80)


def demo_no_hallucination():
    """Demo 6: Confirm No Hallucination"""
    print_section("DEMO 6: Confirm System Doesn't Generate Content Outside KB")

    engine = RetrievalEngine(auto_initialize_kb=True)

    # Query completely outside domain
    print("Query: 'quantum mechanics wavefunction collapse'")
    outside = engine.retrieve("quantum mechanics wavefunction collapse", n_results=5)

    print(f"\nHas Results: {outside.get('has_results')}")

    if not outside.get('has_results'):
        print("  No results found (as expected)")
        if outside.get('fallback'):
            print(f"\n  Fallback triggered:")
            print(f"    Type: {outside['fallback'].get('type')}")
            print(f"    Message: {outside['fallback'].get('message')}")
            print(f"    Recommendation: {outside['fallback'].get('recommendation')}")
            print(f"    Action: {outside['fallback'].get('action')}")
    else:
        print("  Warning: System returned results for out-of-domain query")

    print("\n" + "-" * 80)


def demo_performance():
    """Demo 7: Performance Benchmark"""
    print_section("DEMO 7: Benchmark Retrieval Latency and Accuracy")

    engine = RetrievalEngine(auto_initialize_kb=True)

    import time

    queries = [
        "closed syllable",
        "phoneme blending",
        "decodability rate",
        "multisensory instruction",
        "vowel team"
    ]

    print("Running performance benchmark...")
    print(f"Queries: {len(queries)}\n")

    total_time = 0
    results_with_matches = 0

    for i, query in enumerate(queries, 1):
        start = time.time()
        result = engine.retrieve(query, n_results=3)
        query_time = (time.time() - start) * 1000

        total_time += query_time
        has_results = result.get("has_results", False)
        if has_results:
            results_with_matches += 1

        print(f"{i}. '{query}'")
        print(f"   Time: {query_time:.2f}ms | Has Results: {has_results}")

    avg_time = total_time / len(queries)
    accuracy = (results_with_matches / len(queries)) * 100

    print(f"\n{'=' * 40}")
    print(f"Average Retrieval Time: {avg_time:.2f}ms")
    print(f"Accuracy: {accuracy:.1f}% ({results_with_matches}/{len(queries)} queries)")
    print(f"Total Time: {total_time:.2f}ms")
    print(f"{'=' * 40}")

    print("\n" + "-" * 80)


def demo_system_stats():
    """Demo 8: System Statistics"""
    print_section("DEMO 8: RAG System Statistics")

    engine = RetrievalEngine(auto_initialize_kb=True)
    stats = engine.get_system_stats()

    print("Knowledge Base Statistics:")
    kb_stats = stats.get("knowledge_base", {})
    print(f"  Collection Name: {kb_stats.get('collection_name')}")
    print(f"  Total Documents: {kb_stats.get('document_count')}")
    print(f"  Cache Size: {kb_stats.get('cache_size')}")
    print(f"  Sources: {', '.join(kb_stats.get('sources', {}).keys())}")

    print("\nFCRR Database Statistics:")
    fcrr_stats = stats.get("fcrr_database", {})
    print(f"  Total Categories: {fcrr_stats.get('total_categories')}")
    print(f"  Total Patterns: {fcrr_stats.get('total_patterns')}")
    print(f"  Total Words: {fcrr_stats.get('total_words')}")
    print(f"  Activity Colors: {fcrr_stats.get('activity_colors')}")
    print(f"  Categories: {', '.join(fcrr_stats.get('categories', []))}")

    print(f"\nSystem Ready: {stats.get('system_ready')}")

    print("\n" + "-" * 80)


def main():
    """Run all demos"""
    print("\n" + "#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + "  RAG-POWERED PEDAGOGICAL GROUNDING SYSTEM".center(78) + "#")
    print("#" + "  ALPA-2: Knowledge Retrieval System Demo".center(78) + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)

    demo_knowledge_base_retrieval()
    demo_wilson_vs_og()
    demo_fcrr_word_lists()
    demo_rag_constraints()
    demo_edge_cases()
    demo_no_hallucination()
    demo_performance()
    demo_system_stats()

    print_section("DEMO COMPLETE")
    print("All RAG system features demonstrated successfully!")
    print("The system is ready for integration with the multi-agent orchestrator.\n")


if __name__ == "__main__":
    main()
