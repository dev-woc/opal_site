"""
Shared Scratchpad for Multi-Agent State Management

This module provides a centralized conversation history and state management
system that all agents can access and update. It maintains a complete audit
trail of agent interactions and decisions.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import json


class MessageType(Enum):
    """Types of messages that can be logged in the scratchpad"""
    AGENT_INPUT = "agent_input"
    AGENT_OUTPUT = "agent_output"
    AGENT_THINKING = "agent_thinking"
    SYSTEM_EVENT = "system_event"
    ERROR = "error"


class ScratchpadMessage:
    """Individual message in the scratchpad"""

    def __init__(
        self,
        agent_name: str,
        message_type: MessageType,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.agent_name = agent_name
        self.message_type = message_type
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format"""
        return {
            "agent_name": self.agent_name,
            "message_type": self.message_type.value,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }

    def __repr__(self) -> str:
        return f"<ScratchpadMessage {self.agent_name}:{self.message_type.value} at {self.timestamp}>"


class SharedScratchpad:
    """
    Centralized state management and conversation history for multi-agent system.

    This class provides:
    - Unified conversation history across all agents
    - State persistence and retrieval
    - Agent decision logging for observability
    - Query capabilities for agents to access relevant context
    """

    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.messages: List[ScratchpadMessage] = []
        self.shared_state: Dict[str, Any] = {}

    def add_message(
        self,
        agent_name: str,
        message_type: MessageType,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ScratchpadMessage:
        """
        Add a new message to the scratchpad

        Args:
            agent_name: Name of the agent adding the message
            message_type: Type of message being added
            content: Message content (can be string, dict, etc.)
            metadata: Additional metadata about the message

        Returns:
            The created ScratchpadMessage
        """
        message = ScratchpadMessage(agent_name, message_type, content, metadata)
        self.messages.append(message)

        # Trim history if it exceeds max_history
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]

        return message

    def get_history(
        self,
        agent_name: Optional[str] = None,
        message_type: Optional[MessageType] = None,
        limit: Optional[int] = None
    ) -> List[ScratchpadMessage]:
        """
        Retrieve conversation history with optional filtering

        Args:
            agent_name: Filter by specific agent (None = all agents)
            message_type: Filter by message type (None = all types)
            limit: Maximum number of messages to return (None = all)

        Returns:
            List of matching ScratchpadMessage objects
        """
        filtered_messages = self.messages

        if agent_name:
            filtered_messages = [m for m in filtered_messages if m.agent_name == agent_name]

        if message_type:
            filtered_messages = [m for m in filtered_messages if m.message_type == message_type]

        if limit:
            filtered_messages = filtered_messages[-limit:]

        return filtered_messages

    def update_state(self, key: str, value: Any, agent_name: str) -> None:
        """
        Update shared state variable

        Args:
            key: State variable key
            value: New value for the state variable
            agent_name: Name of agent updating the state
        """
        self.shared_state[key] = value

        # Log state update
        self.add_message(
            agent_name=agent_name,
            message_type=MessageType.SYSTEM_EVENT,
            content=f"Updated shared state: {key}",
            metadata={"key": key, "value": value}
        )

    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Retrieve shared state variable

        Args:
            key: State variable key
            default: Default value if key doesn't exist

        Returns:
            State variable value or default
        """
        return self.shared_state.get(key, default)

    def get_conversation_context(self, max_messages: int = 10) -> str:
        """
        Get formatted conversation context for agent prompts

        Args:
            max_messages: Maximum number of recent messages to include

        Returns:
            Formatted string with conversation history
        """
        recent_messages = self.messages[-max_messages:]

        context_lines = ["=== Conversation History ==="]
        for msg in recent_messages:
            context_lines.append(
                f"[{msg.timestamp}] {msg.agent_name} ({msg.message_type.value}): {msg.content}"
            )
        context_lines.append("=== End History ===\n")

        return "\n".join(context_lines)

    def export_history(self) -> str:
        """
        Export complete history as JSON string

        Returns:
            JSON string of all messages
        """
        return json.dumps([msg.to_dict() for msg in self.messages], indent=2)

    def clear(self) -> None:
        """Clear all messages and state (use with caution)"""
        self.messages.clear()
        self.shared_state.clear()

    def __repr__(self) -> str:
        return f"<SharedScratchpad messages={len(self.messages)} state_vars={len(self.shared_state)}>"
