# Agentic Literacy Pipeline App

An agentic pipeline designed to synthesize Wilson Reading System (WRS), Orton-Gillingham (OG), UFLI Foundations, and FCRR into a cohesive system for generating interactive digital and high-fidelity print materials.

## Overview

This project implements a multi-agent orchestration system for structured literacy instruction, combining:
- Curriculum planning and lesson decomposition
- Narrative generation with phonetic validation
- Diagnostic analysis for student errors
- Digital interactivity with gamification
- Automated print production

## Tech Stack

- **Orchestration**: LangChain or CrewAI
- **Generation**: GPT-4o with strict RAG constraints, Lexial databases
- **Phonetic Auditing**: NVIDIA NeMo (G2P-Conformer), CMU Pronouncing Dictionary
- **Print & Layout**: Python (ReportLab, WeasyPrint), Canva API, MagicSchool

## Features

### 1. Multi-Agent Orchestration
- Curriculum Planner: Decomposes learning objectives into structured lesson plans
- Narrative Architect: Generates engaging stories using strictly allowed phonemes
- Diagnostic Specialist: Analyzes student errors to suggest prescriptive teaching focuses
- Shared scratchpad for unified state management

### 2. RAG-Powered Pedagogical Grounding
- Retrieval-Augmented Generation for validated science grounding
- Structured Literacy documentation integration
- FCRR resource database word lists and activities

### 3. Automated Phonetic Verification
- Grapheme-to-Phoneme (G2P) conversion
- 95% decodability rate enforcement
- Orthographic rules validation

### 4. Digital Interactivity & Gamification
- Virtual blending boards with letter tiles
- Text-to-Speech auditory feedback
- Mobile haptic tapping for multisensory learning
- Adaptive difficulty adjustment

### 5. Programmatic Print Generation
- Automated print production for handwriting practice
- ReportLab pixel-precise layout
- Canva API integration for templates

## Project Structure

```
app/
├── agents/
│   ├── planner.py        # Curriculum Planner logic
│   ├── architect.py      # Narrative Architect (GPT-4o + Lexial)
│   ├── auditor.py        # Phonetic Auditor (NeMo G2P)
│   ├── engineer.py       # Activity Engineer
│   └── diagnostic.py     # Diagnostic Specialist
├── retrieval/
│   └── vector_db/        # RAG embeddings (Wilson/OG/UFLI rules)
├── generation/
│   ├── digital_ui/       # Virtual blending boards & TTS/Haptics
│   └── print_scripts/    # ReportLab & WeasyPrint PDF generators
└── main.py               # LangChain/CrewAI orchestration core
```

## Getting Started

Run the initialization script to set up the development environment:

```bash
./init.sh
```

## Success Criteria

- Texts maintain a strict 95% decodability rate
- System is fully observable with logged AI decisions
- Reduces educator "prompting gap" through Flipped Interaction patterns
- Small teams (under 7 agents) operate without conflicting assumptions
