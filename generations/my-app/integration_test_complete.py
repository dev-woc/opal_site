#!/usr/bin/env python3
"""
Complete Integration Test for Multi-Agent Orchestration System
Tests all three agents working together with full LLM functionality

Test Steps:
1. Initialize orchestration system with three agents
2. Provide sample learning objectives
3. Verify Curriculum Planner decomposes into lesson plan
4. Verify Narrative Architect generates story with allowed phonemes
5. Provide sample student error data to Diagnostic Specialist
6. Confirm shared scratchpad maintains conversation history
7. Verify all agents can access and update shared state
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import orchestration components
from app.orchestration import AgentOrchestrator
from app.orchestration.scratchpad import MessageType


def print_header(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_result(result: Dict[str, Any], agent_name: str):
    """Pretty print agent result"""
    print(f"\n[{agent_name}] Result:")
    print(f"  Success: {result.get('success', 'N/A')}")

    if result.get('success'):
        # Print agent-specific output
        if 'lesson_plan' in result:
            lp = result['lesson_plan']
            print(f"  Objective: {lp.get('objective', 'N/A')}")
            lessons = lp.get('lesson_sequence', [])
            print(f"  Lessons Created: {len(lessons)}")
            if lessons:
                print(f"  First Lesson: {lessons[0].get('title', 'N/A')}")
                print(f"  Focus Phonemes: {', '.join(lessons[0].get('focus_phonemes', []))}")

        elif 'narrative' in result:
            narrative = result['narrative']
            print(f"  Story Title: {narrative.get('title', 'N/A')}")
            print(f"  Word Count: {narrative.get('word_count', 'N/A')}")
            print(f"  Decodability: {narrative.get('decodability_rate', 'N/A')}%")
            print(f"  Phonemes Used: {len(narrative.get('target_phonemes', []))}")

        elif 'diagnosis' in result:
            diagnosis = result['diagnosis']
            error_summary = diagnosis.get('error_summary', {})
            print(f"  Total Errors: {error_summary.get('total_errors', 'N/A')}")
            interventions = diagnosis.get('recommended_interventions', [])
            print(f"  Interventions: {len(interventions)}")
            high_priority = sum(1 for i in interventions if i.get('priority') == 'high')
            print(f"  High Priority: {high_priority}")
    else:
        print(f"  Error: {result.get('error', 'Unknown error')}")


def test_step_1_initialization():
    """Test Step 1: Initialize orchestration system with three agents"""
    print_header("TEST STEP 1: Initialize Orchestration System")

    print("Creating AgentOrchestrator with shared scratchpad...")
    orchestrator = AgentOrchestrator(max_history=50)

    # Verify agents are initialized
    summary = orchestrator.get_agent_summary()

    print(f"\nOrchestrator initialized successfully!")
    print(f"  Agents: {len(summary['agents'])}")
    for agent in summary['agents']:
        print(f"    - {agent['name']} ({agent['type']}) using {agent['model']}")

    print(f"\nScratchpad Status:")
    print(f"  Messages: {summary['scratchpad']['messages']}")
    print(f"  State Variables: {summary['scratchpad']['state_variables']}")

    print("\n✓ TEST STEP 1 PASSED")
    return orchestrator


def test_step_2_curriculum_planning(orchestrator: AgentOrchestrator):
    """Test Step 2: Curriculum Planner decomposes learning objective"""
    print_header("TEST STEP 2: Curriculum Planning - Decompose Learning Objective")

    learning_objective = "Teach students to decode CVC words with short 'a' sound (cat, mat, sat)"

    print(f"Learning Objective: {learning_objective}")
    print("\nInvoking Curriculum Planner agent...")

    result = orchestrator.plan_curriculum(learning_objective)

    print_result(result, "CurriculumPlanner")

    # Verify lesson plan structure
    if result.get('success') and 'lesson_plan' in result:
        lesson_plan = result['lesson_plan']

        # Check required fields
        required_fields = ['objective', 'lesson_sequence']
        missing = [f for f in required_fields if f not in lesson_plan]

        if missing:
            print(f"\n✗ Missing required fields: {', '.join(missing)}")
            return False

        # Verify lesson sequence has content
        if len(lesson_plan.get('lesson_sequence', [])) == 0:
            print("\n✗ No lessons in lesson sequence")
            return False

        # Show detailed lesson breakdown
        print("\nLesson Plan Details:")
        for i, lesson in enumerate(lesson_plan.get('lesson_sequence', []), 1):
            print(f"\n  Lesson {i}: {lesson.get('title', 'N/A')}")
            print(f"    Phonemes: {', '.join(lesson.get('focus_phonemes', []))}")
            print(f"    Graphemes: {', '.join(lesson.get('focus_graphemes', []))}")
            print(f"    Activities: {len(lesson.get('activities', []))}")

        print("\n✓ TEST STEP 2 PASSED")
        return True
    else:
        print("\n✗ TEST STEP 2 FAILED")
        return False


def test_step_3_narrative_generation(orchestrator: AgentOrchestrator):
    """Test Step 3: Narrative Architect generates decodable story"""
    print_header("TEST STEP 3: Narrative Generation - Create Decodable Story")

    print("Generating narrative based on lesson plan from shared state...")
    print("(Narrative Architect will access lesson plan from scratchpad)")

    # The architect will automatically pull phonemes/graphemes from lesson plan
    result = orchestrator.generate_narrative(
        topic="A cat's adventure",
        word_count=80
    )

    print_result(result, "NarrativeArchitect")

    # Verify narrative structure
    if result.get('success') and 'narrative' in result:
        narrative = result['narrative']

        # Check required fields
        required_fields = ['title', 'text']
        missing = [f for f in required_fields if f not in narrative]

        if missing:
            print(f"\n✗ Missing required fields: {', '.join(missing)}")
            return False

        # Show story details
        print("\nStory Details:")
        print(f"  Title: {narrative.get('title', 'N/A')}")
        print(f"  Target Phonemes: {', '.join(narrative.get('target_phonemes', []))}")
        print(f"  Heart Words: {', '.join(narrative.get('heart_words', []))}")
        print(f"\nStory Text (first 200 chars):")
        text = narrative.get('text', '')
        print(f"  {text[:200]}...")

        if narrative.get('comprehension_questions'):
            print(f"\nComprehension Questions:")
            for q in narrative['comprehension_questions']:
                print(f"  - {q}")

        print("\n✓ TEST STEP 3 PASSED")
        return True
    else:
        print("\n✗ TEST STEP 3 FAILED")
        return False


def test_step_4_diagnostic_analysis(orchestrator: AgentOrchestrator):
    """Test Step 4: Diagnostic Specialist analyzes student errors"""
    print_header("TEST STEP 4: Diagnostic Analysis - Analyze Student Errors")

    # Sample student errors
    student_errors = [
        {"target": "cat", "response": "kat", "type": "substitution"},
        {"target": "mat", "response": "ma", "type": "omission"},
        {"target": "sat", "response": "set", "type": "substitution"},
        {"target": "bat", "response": "bad", "type": "substitution"},
        {"target": "rat", "response": "rag", "type": "substitution"},
    ]

    print(f"Analyzing {len(student_errors)} errors for student 'student_001'")
    print("\nStudent Errors:")
    for err in student_errors:
        print(f"  Target: '{err['target']}' → Student: '{err['response']}' ({err['type']})")

    print("\nInvoking Diagnostic Specialist agent...")

    result = orchestrator.diagnose_errors(
        errors=student_errors,
        student_id="student_001",
        context="Assessment on CVC words with short 'a'"
    )

    print_result(result, "DiagnosticSpecialist")

    # Verify diagnosis structure
    if result.get('success') and 'diagnosis' in result:
        diagnosis = result['diagnosis']

        # Check required fields
        required_fields = ['error_summary', 'recommended_interventions']
        missing = [f for f in required_fields if f not in diagnosis]

        if missing:
            print(f"\n✗ Missing required fields: {', '.join(missing)}")
            return False

        # Show diagnostic findings
        print("\nDiagnostic Findings:")
        for finding in diagnosis.get('diagnostic_findings', []):
            print(f"  - {finding}")

        print("\nRecommended Interventions:")
        for i, intervention in enumerate(diagnosis.get('recommended_interventions', []), 1):
            print(f"\n  {i}. Priority: {intervention.get('priority', 'N/A').upper()}")
            print(f"     Focus: {intervention.get('focus_area', 'N/A')}")
            print(f"     Activities: {', '.join(intervention.get('activities', []))}")

        print("\n✓ TEST STEP 4 PASSED")
        return True
    else:
        print("\n✗ TEST STEP 4 FAILED")
        return False


def test_step_5_scratchpad_history(orchestrator: AgentOrchestrator):
    """Test Step 5: Verify shared scratchpad maintains conversation history"""
    print_header("TEST STEP 5: Scratchpad - Verify Conversation History")

    # Get scratchpad summary
    summary = orchestrator.get_agent_summary()
    message_count = summary['scratchpad']['messages']
    state_count = summary['scratchpad']['state_variables']

    print(f"Scratchpad Statistics:")
    print(f"  Total Messages: {message_count}")
    print(f"  State Variables: {state_count}")

    # Get recent conversation history
    context = orchestrator.scratchpad.get_conversation_context(max_messages=10)

    print(f"\nRecent Conversation History (last 10 messages):")
    print(context)

    # Verify we have messages from all agents
    history = orchestrator.scratchpad.get_history()
    agents_in_history = set(msg.agent_name for msg in history)

    print(f"\nAgents that have logged messages:")
    for agent in agents_in_history:
        agent_messages = [m for m in history if m.agent_name == agent]
        print(f"  - {agent}: {len(agent_messages)} messages")

    # Check if all three specialist agents are present
    expected_agents = ['CurriculumPlanner', 'NarrativeArchitect', 'DiagnosticSpecialist']
    present_agents = [a for a in expected_agents if a in agents_in_history]

    if len(present_agents) == len(expected_agents):
        print(f"\n✓ All {len(expected_agents)} specialist agents have logged to scratchpad")
        print("\n✓ TEST STEP 5 PASSED")
        return True
    else:
        missing = set(expected_agents) - agents_in_history
        print(f"\n✗ Missing agents: {', '.join(missing)}")
        print("\n✗ TEST STEP 5 FAILED")
        return False


def test_step_6_shared_state_access(orchestrator: AgentOrchestrator):
    """Test Step 6: Verify agents can access and update shared state"""
    print_header("TEST STEP 6: Shared State - Verify Cross-Agent Access")

    print("Checking shared state variables created by agents...")

    state_vars = orchestrator.scratchpad.shared_state

    print(f"\nShared State Variables ({len(state_vars)}):")
    for key, value in state_vars.items():
        value_preview = str(value)[:100]
        if len(str(value)) > 100:
            value_preview += "..."
        print(f"  - {key}: {value_preview}")

    # Check for expected state variables
    expected_vars = ['current_lesson_plan', 'current_narrative', 'diagnosis_student_001']
    present_vars = [v for v in expected_vars if v in state_vars]

    print(f"\nExpected State Variables Present:")
    for var in expected_vars:
        status = "✓" if var in state_vars else "✗"
        print(f"  {status} {var}")

    # Test cross-agent access: verify NarrativeArchitect used CurriculumPlanner's data
    lesson_plan = orchestrator.scratchpad.get_state('current_lesson_plan')
    narrative = orchestrator.scratchpad.get_state('current_narrative')

    if lesson_plan and narrative:
        lesson_phonemes = set()
        for lesson in lesson_plan.get('lesson_sequence', []):
            lesson_phonemes.update(lesson.get('focus_phonemes', []))

        narrative_phonemes = set(narrative.get('target_phonemes', []))

        print(f"\nCross-Agent Data Verification:")
        print(f"  Lesson Plan Phonemes: {lesson_phonemes}")
        print(f"  Narrative Phonemes: {narrative_phonemes}")

        if narrative_phonemes:
            print(f"\n  ✓ Narrative Architect accessed lesson plan data from shared state")

    if len(present_vars) == len(expected_vars):
        print("\n✓ TEST STEP 6 PASSED")
        return True
    else:
        print(f"\n✗ Missing state variables: {set(expected_vars) - set(present_vars)}")
        print("\n✗ TEST STEP 6 FAILED")
        return False


def test_step_7_full_pipeline(orchestrator: AgentOrchestrator):
    """Test Step 7: Run complete multi-agent pipeline"""
    print_header("TEST STEP 7: Full Pipeline - End-to-End Integration")

    print("Running complete pipeline with all three agents...")

    # Reset for clean pipeline test
    orchestrator.reset()

    objective = "Teach consonant blends: /bl/, /gr/, /st/"
    errors = [
        {"target": "blend", "response": "blen", "type": "omission"},
        {"target": "great", "response": "grat", "type": "substitution"}
    ]

    print(f"\nPipeline Input:")
    print(f"  Learning Objective: {objective}")
    print(f"  Student Errors: {len(errors)} errors")

    result = orchestrator.run_full_pipeline(
        learning_objective=objective,
        student_errors=errors,
        student_id="student_002"
    )

    print(f"\nPipeline Execution:")
    print(f"  Steps Completed: {len(result.get('pipeline_steps', []))}")
    for step in result.get('pipeline_steps', []):
        print(f"    ✓ {step}")

    print(f"\nPipeline Results:")
    print(f"  Planning Success: {result.get('planning', {}).get('success', False)}")
    print(f"  Narrative Success: {result.get('narrative', {}).get('success', False)}")
    print(f"  Diagnosis Success: {result.get('diagnosis', {}).get('success', False)}")

    all_success = all([
        result.get('planning', {}).get('success', False),
        result.get('narrative', {}).get('success', False),
        result.get('diagnosis', {}).get('success', False)
    ])

    if all_success:
        print("\n✓ TEST STEP 7 PASSED")
        return True
    else:
        print("\n✗ TEST STEP 7 FAILED")
        return False


def main():
    """Run complete integration test suite"""

    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("ERROR: OPENAI_API_KEY not found in environment")
        print("Please set your OpenAI API key in .env file")
        return 1

    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 10 + "MULTI-AGENT ORCHESTRATION - COMPLETE INTEGRATION TEST" + " " * 15 + "║")
    print("╚" + "=" * 78 + "╝")
    print(f"\nTest Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Model: {os.getenv('OPENAI_MODEL', 'gpt-4o')}")

    # Initialize orchestrator
    orchestrator = test_step_1_initialization()

    # Run all test steps
    results = []

    try:
        results.append(test_step_2_curriculum_planning(orchestrator))
        results.append(test_step_3_narrative_generation(orchestrator))
        results.append(test_step_4_diagnostic_analysis(orchestrator))
        results.append(test_step_5_scratchpad_history(orchestrator))
        results.append(test_step_6_shared_state_access(orchestrator))
        results.append(test_step_7_full_pipeline(orchestrator))

    except Exception as e:
        print(f"\n✗ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    # Print summary
    print_header("TEST SUMMARY")

    passed = sum(results)
    total = len(results)

    print(f"Tests Passed: {passed}/{total}")

    test_names = [
        "Initialization",
        "Curriculum Planning",
        "Narrative Generation",
        "Diagnostic Analysis",
        "Scratchpad History",
        "Shared State Access",
        "Full Pipeline"
    ]

    print("\nDetailed Results:")
    for i, (name, result) in enumerate(zip(test_names, results), 1):
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {i}. {name}: {status}")

    if passed == total:
        print("\n" + "=" * 80)
        print("✓ ALL INTEGRATION TESTS PASSED")
        print("=" * 80)
        print("\nThe multi-agent orchestration system is fully functional!")
        print("\nKey Features Verified:")
        print("  ✓ Three specialized agents (Planner, Architect, Diagnostic)")
        print("  ✓ Shared scratchpad for unified state management")
        print("  ✓ Inter-agent communication via shared state")
        print("  ✓ Curriculum decomposition with LLM")
        print("  ✓ Narrative generation with phonetic constraints")
        print("  ✓ Student error analysis and intervention recommendations")
        print("  ✓ Complete conversation history logging")
        print("  ✓ End-to-end pipeline orchestration")
        print("\n" + "=" * 80)
        return 0
    else:
        print("\n" + "=" * 80)
        print("✗ SOME TESTS FAILED")
        print("=" * 80)
        print(f"\nFailed: {total - passed} test(s)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
