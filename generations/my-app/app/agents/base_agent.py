"""
Base Agent Class

Provides common functionality for all agents in the multi-agent system,
including scratchpad access and LLM interaction patterns.
"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.orchestration.scratchpad import SharedScratchpad, MessageType
import os


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.

    Each agent must implement:
    - get_system_prompt(): Returns the agent's specialized instructions
    - process(): Executes the agent's core logic
    """

    def __init__(
        self,
        name: str,
        scratchpad: SharedScratchpad,
        model_name: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        Initialize base agent

        Args:
            name: Agent's unique identifier
            scratchpad: Shared scratchpad for state management
            model_name: LLM model to use (defaults to env var)
            temperature: LLM temperature setting
        """
        self.name = name
        self.scratchpad = scratchpad
        self.model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-4o")
        self.temperature = temperature

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # Log agent initialization
        self.log_message(
            MessageType.SYSTEM_EVENT,
            f"Agent {self.name} initialized with model {self.model_name}"
        )

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Return the agent's system prompt with role-specific instructions.

        This must be implemented by each specialized agent.
        """
        pass

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's core processing logic.

        Args:
            input_data: Input parameters for the agent's task

        Returns:
            Dictionary containing the agent's output
        """
        pass

    def log_message(
        self,
        message_type: MessageType,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a message to the shared scratchpad

        Args:
            message_type: Type of message
            content: Message content
            metadata: Additional metadata
        """
        self.scratchpad.add_message(
            agent_name=self.name,
            message_type=message_type,
            content=content,
            metadata=metadata
        )

    def get_conversation_context(self, max_messages: int = 10) -> str:
        """
        Retrieve recent conversation context from scratchpad

        Args:
            max_messages: Number of recent messages to retrieve

        Returns:
            Formatted conversation context string
        """
        return self.scratchpad.get_conversation_context(max_messages)

    def invoke_llm(
        self,
        user_prompt: str,
        include_context: bool = True,
        context_messages: int = 10
    ) -> str:
        """
        Invoke the LLM with agent's system prompt and user input

        Args:
            user_prompt: The user's input/query
            include_context: Whether to include conversation context
            context_messages: Number of context messages to include

        Returns:
            LLM's response string
        """
        # Build prompt with system instructions
        system_prompt = self.get_system_prompt()

        # Escape curly braces in system prompt to prevent template variable errors
        # This is needed because JSON examples in prompts use {} which ChatPromptTemplate
        # tries to interpret as variables
        system_prompt = system_prompt.replace("{", "{{").replace("}", "}}")

        # Add conversation context if requested
        if include_context:
            context = self.get_conversation_context(context_messages)
            user_prompt = f"{context}\n\n{user_prompt}"

        # Create chat prompt template
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{input}")
        ])

        # Invoke LLM
        chain = prompt_template | self.llm
        response = chain.invoke({"input": user_prompt})

        # Extract text content
        response_text = response.content if hasattr(response, 'content') else str(response)

        # Log the interaction
        self.log_message(MessageType.AGENT_INPUT, user_prompt)
        self.log_message(MessageType.AGENT_OUTPUT, response_text)

        return response_text

    def update_shared_state(self, key: str, value: Any) -> None:
        """
        Update a variable in shared state

        Args:
            key: State variable name
            value: New value
        """
        self.scratchpad.update_state(key, value, self.name)

    def get_shared_state(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a variable from shared state

        Args:
            key: State variable name
            default: Default value if not found

        Returns:
            State variable value
        """
        return self.scratchpad.get_state(key, default)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} model={self.model_name}>"
