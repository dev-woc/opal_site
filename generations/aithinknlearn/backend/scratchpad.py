"""
Shared Scratchpad for Multi-Agent State Management

This module provides a centralized state management system for the multi-agent
orchestration pipeline. All agents share access to this scratchpad to maintain
unified context and decision history.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Enumeration of agent types in the system"""
    CURRICULUM_PLANNER = "curriculum_planner"
    NARRATIVE_ARCHITECT = "narrative_architect"
    DIAGNOSTIC_SPECIALIST = "diagnostic_specialist"


@dataclass
class AgentDecision:
    """Represents a single decision made by an agent"""
    agent_type: str
    timestamp: str
    decision: str
    reasoning: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert decision to dictionary"""
        return asdict(self)


@dataclass
class ScratchpadEntry:
    """Represents an entry in the scratchpad"""
    entry_id: str
    agent_type: str
    timestamp: str
    content: str
    entry_type: str  # 'decision', 'observation', 'plan', 'result'
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary"""
        return asdict(self)


class SharedScratchpad:
    """
    Shared scratchpad for multi-agent state management.

    Provides:
    - Unified conversation history across all agents
    - Decision logging for teacher review
    - State consistency mechanisms
    - Agent interaction tracking
    """

    def __init__(self):
        """Initialize the shared scratchpad"""
        self.entries: List[ScratchpadEntry] = []
        self.decisions: List[AgentDecision] = []
        self.state: Dict[str, Any] = {
            "learning_objectives": [],
            "lesson_plan": {},
            "story_content": "",
            "allowed_phonemes": [],
            "student_errors": [],
            "teaching_focuses": [],
            "curriculum_stage": "initial",
        }
        self.conversation_history: List[Dict[str, str]] = []
        self._entry_counter = 0
        logger.info("SharedScratchpad initialized")

    def add_entry(
        self,
        agent_type: AgentType,
        content: str,
        entry_type: str = "observation",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add an entry to the scratchpad

        Args:
            agent_type: Type of agent making the entry
            content: Content of the entry
            entry_type: Type of entry ('decision', 'observation', 'plan', 'result')
            metadata: Additional metadata

        Returns:
            Entry ID
        """
        self._entry_counter += 1
        entry_id = f"entry_{self._entry_counter}_{agent_type.value}"

        entry = ScratchpadEntry(
            entry_id=entry_id,
            agent_type=agent_type.value,
            timestamp=datetime.now().isoformat(),
            content=content,
            entry_type=entry_type,
            metadata=metadata or {}
        )

        self.entries.append(entry)
        logger.info(f"Entry added: {entry_id} by {agent_type.value}")

        return entry_id

    def log_decision(
        self,
        agent_type: AgentType,
        decision: str,
        reasoning: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an agent decision for teacher review

        Args:
            agent_type: Type of agent making the decision
            decision: The decision made
            reasoning: Reasoning behind the decision
            metadata: Additional metadata
        """
        agent_decision = AgentDecision(
            agent_type=agent_type.value,
            timestamp=datetime.now().isoformat(),
            decision=decision,
            reasoning=reasoning,
            metadata=metadata or {}
        )

        self.decisions.append(agent_decision)

        # Also add to entries for unified history
        self.add_entry(
            agent_type=agent_type,
            content=f"DECISION: {decision}",
            entry_type="decision",
            metadata={"reasoning": reasoning, **(metadata or {})}
        )

        logger.info(f"Decision logged by {agent_type.value}: {decision}")

    def update_state(self, key: str, value: Any, agent_type: AgentType) -> None:
        """
        Update shared state

        Args:
            key: State key to update
            value: New value
            agent_type: Agent making the update
        """
        old_value = self.state.get(key)
        self.state[key] = value

        self.add_entry(
            agent_type=agent_type,
            content=f"Updated state '{key}': {old_value} -> {value}",
            entry_type="observation",
            metadata={"state_key": key, "old_value": str(old_value), "new_value": str(value)}
        )

        logger.info(f"State updated by {agent_type.value}: {key} = {value}")

    def get_state(self, key: Optional[str] = None) -> Any:
        """
        Get current state

        Args:
            key: Specific state key, or None to get all state

        Returns:
            State value or entire state dict
        """
        if key is None:
            return self.state.copy()
        return self.state.get(key)

    def add_conversation_message(self, role: str, content: str) -> None:
        """
        Add a message to conversation history

        Args:
            role: Role of the speaker (user, assistant, system)
            content: Message content
        """
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        logger.info(f"Conversation message added: {role}")

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the full conversation history"""
        return self.conversation_history.copy()

    def get_entries_by_agent(self, agent_type: AgentType) -> List[ScratchpadEntry]:
        """Get all entries by a specific agent"""
        return [e for e in self.entries if e.agent_type == agent_type.value]

    def get_entries_by_type(self, entry_type: str) -> List[ScratchpadEntry]:
        """Get all entries of a specific type"""
        return [e for e in self.entries if e.entry_type == entry_type]

    def get_all_decisions(self) -> List[AgentDecision]:
        """Get all logged decisions"""
        return self.decisions.copy()

    def get_decisions_by_agent(self, agent_type: AgentType) -> List[AgentDecision]:
        """Get decisions by a specific agent"""
        return [d for d in self.decisions if d.agent_type == agent_type.value]

    def export_log(self) -> Dict[str, Any]:
        """
        Export complete scratchpad log for teacher review

        Returns:
            Dictionary containing all entries, decisions, and state
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "total_entries": len(self.entries),
            "total_decisions": len(self.decisions),
            "entries": [e.to_dict() for e in self.entries],
            "decisions": [d.to_dict() for d in self.decisions],
            "state": self.state,
            "conversation_history": self.conversation_history
        }

    def clear(self) -> None:
        """Clear the scratchpad (use with caution)"""
        self.entries.clear()
        self.decisions.clear()
        self.conversation_history.clear()
        self.state = {
            "learning_objectives": [],
            "lesson_plan": {},
            "story_content": "",
            "allowed_phonemes": [],
            "student_errors": [],
            "teaching_focuses": [],
            "curriculum_stage": "initial",
        }
        self._entry_counter = 0
        logger.info("Scratchpad cleared")

    def __repr__(self) -> str:
        """String representation"""
        return f"SharedScratchpad(entries={len(self.entries)}, decisions={len(self.decisions)})"
