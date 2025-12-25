"""
Voice Command Handler with Unified AI Command Processor
Handles voice input processing and routes commands to appropriate handlers
"""

import logging
import json
from typing import Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime
import re


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommandType(Enum):
    """Enumeration of supported command types"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    DEBUGGING = "debugging"
    REFACTORING = "refactoring"
    QUERY = "query"
    HELP = "help"
    UNKNOWN = "unknown"


class ExecutionStatus(Enum):
    """Enumeration of command execution statuses"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class VoiceCommand:
    """Data class representing a voice command"""
    raw_input: str
    command_type: CommandType
    content: str
    timestamp: str
    context: Optional[Dict[str, Any]] = None
    status: ExecutionStatus = ExecutionStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert command to dictionary representation"""
        data = asdict(self)
        data['command_type'] = self.command_type.value
        data['status'] = self.status.value
        return data


class UnifiedAICommandProcessor:
    """
    Unified AI command processor that handles voice commands and routes them
    to appropriate handlers for execution
    """

    def __init__(self):
        """Initialize the command processor with default handlers"""
        self.handlers: Dict[CommandType, Callable] = {}
        self.command_history: list = []
        self.max_history = 100
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default command handlers"""
        self.register_handler(CommandType.CODE_GENERATION, self._handle_code_generation)
        self.register_handler(CommandType.CODE_REVIEW, self._handle_code_review)
        self.register_handler(CommandType.DOCUMENTATION, self._handle_documentation)
        self.register_handler(CommandType.TESTING, self._handle_testing)
        self.register_handler(CommandType.DEBUGGING, self._handle_debugging)
        self.register_handler(CommandType.REFACTORING, self._handle_refactoring)
        self.register_handler(CommandType.QUERY, self._handle_query)
        self.register_handler(CommandType.HELP, self._handle_help)
        self.register_handler(CommandType.UNKNOWN, self._handle_unknown)

    def register_handler(self, command_type: CommandType, handler: Callable) -> None:
        """
        Register a custom handler for a command type

        Args:
            command_type: The command type to register
            handler: The handler function to associate with the command type
        """
        self.handlers[command_type] = handler
        logger.info(f"Registered handler for {command_type.value}")

    def _classify_command(self, text: str) -> CommandType:
        """
        Classify the command type based on input text

        Args:
            text: The input text to classify

        Returns:
            CommandType: The classified command type
        """
        text_lower = text.lower()

        # Define keyword patterns for each command type
        patterns = {
            CommandType.CODE_GENERATION: [
                r'\b(generate|create|write|make)\s+(code|function|class|method|script)',
                r'\b(code)\s+(for|to)\s+',
                r'\bgenerate\s+',
            ],
            CommandType.CODE_REVIEW: [
                r'\b(review|analyze|check|audit|inspect)\s+(code|this)',
                r'\b(code)\s+(review|analysis)',
            ],
            CommandType.DOCUMENTATION: [
                r'\b(document|explain|describe|comment)\s+(code|this|function)',
                r'\b(documentation|docstring|comments?)',
            ],
            CommandType.TESTING: [
                r'\b(test|unit\s+test|write\s+test)',
                r'\b(test)\s+(for|this)',
                r'\b(create|write)\s+(test|tests)',
            ],
            CommandType.DEBUGGING: [
                r'\b(debug|fix|troubleshoot|error|bug)',
                r'\b(what\'?s\s+)?wrong\b',
                r'\b(fix|solve)\s+(this|the)',
            ],
            CommandType.REFACTORING: [
                r'\b(refactor|optimize|improve|clean\s+up)',
                r'\b(improve|optimization|refactor)',
            ],
            CommandType.QUERY: [
                r'\b(what|how|when|where|why|explain)',
                r'\b(tell|show|list|get)\s+',
            ],
            CommandType.HELP: [
                r'\b(help|assist|support|guide)',
                r'\bwhat\s+can\s+you\s+do',
            ],
        }

        for cmd_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, text_lower):
                    return cmd_type

        return CommandType.UNKNOWN

    def parse_command(self, raw_input: str) -> VoiceCommand:
        """
        Parse voice input and create a VoiceCommand object

        Args:
            raw_input: The raw voice input text

        Returns:
            VoiceCommand: The parsed command object
        """
        command_type = self._classify_command(raw_input)
        timestamp = datetime.utcnow().isoformat() + "Z"

        command = VoiceCommand(
            raw_input=raw_input,
            command_type=command_type,
            content=raw_input,
            timestamp=timestamp,
        )

        logger.info(f"Parsed command: {command_type.value}")
        return command

    def process_command(self, voice_command: VoiceCommand) -> VoiceCommand:
        """
        Process a voice command through the unified processor

        Args:
            voice_command: The VoiceCommand to process

        Returns:
            VoiceCommand: The processed command with result/error
        """
        try:
            voice_command.status = ExecutionStatus.PROCESSING

            # Get the appropriate handler
            handler = self.handlers.get(
                voice_command.command_type,
                self.handlers[CommandType.UNKNOWN]
            )

            # Execute the handler
            result = handler(voice_command)
            voice_command.result = result
            voice_command.status = ExecutionStatus.SUCCESS

            logger.info(f"Command processed successfully: {voice_command.command_type.value}")

        except Exception as e:
            voice_command.status = ExecutionStatus.FAILED
            voice_command.error = str(e)
            logger.error(f"Error processing command: {str(e)}")

        # Add to history
        self._add_to_history(voice_command)
        return voice_command

    def execute(self, raw_input: str) -> VoiceCommand:
        """
        Execute a voice command from raw input string

        Args:
            raw_input: The raw voice input text

        Returns:
            VoiceCommand: The executed command with result/error
        """
        command = self.parse_command(raw_input)
        return self.process_command(command)

    def _add_to_history(self, command: VoiceCommand) -> None:
        """Add command to history, maintaining max history size"""
        self.command_history.append(command)
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)

    def get_history(self, limit: Optional[int] = None) -> list:
        """
        Get command history

        Args:
            limit: Maximum number of commands to return

        Returns:
            list: List of command dictionaries
        """
        history = [cmd.to_dict() for cmd in self.command_history]
        if limit:
            return history[-limit:]
        return history

    def clear_history(self) -> None:
        """Clear the command history"""
        self.command_history.clear()
        logger.info("Command history cleared")

    # Default handler implementations
    @staticmethod
    def _handle_code_generation(command: VoiceCommand) -> str:
        """Handle code generation requests"""
        return f"Code generation request received: {command.content}"

    @staticmethod
    def _handle_code_review(command: VoiceCommand) -> str:
        """Handle code review requests"""
        return f"Code review initiated for: {command.content}"

    @staticmethod
    def _handle_documentation(command: VoiceCommand) -> str:
        """Handle documentation requests"""
        return f"Documentation generation started for: {command.content}"

    @staticmethod
    def _handle_testing(command: VoiceCommand) -> str:
        """Handle testing requests"""
        return f"Test generation requested for: {command.content}"

    @staticmethod
    def _handle_debugging(command: VoiceCommand) -> str:
        """Handle debugging requests"""
        return f"Debugging analysis started for: {command.content}"

    @staticmethod
    def _handle_refactoring(command: VoiceCommand) -> str:
        """Handle refactoring requests"""
        return f"Refactoring suggestions generated for: {command.content}"

    @staticmethod
    def _handle_query(command: VoiceCommand) -> str:
        """Handle query requests"""
        return f"Query response: {command.content}"

    @staticmethod
    def _handle_help(command: VoiceCommand) -> str:
        """Handle help requests"""
        return "Available commands: code_generation, code_review, documentation, testing, debugging, refactoring, query"

    @staticmethod
    def _handle_unknown(command: VoiceCommand) -> str:
        """Handle unknown commands"""
        return f"Command not recognized: {command.content}. Use 'help' for available commands."


class VoiceCommandHandler:
    """
    Main voice command handler interface that provides a simple API
    for voice input processing
    """

    def __init__(self):
        """Initialize the voice command handler"""
        self.processor = UnifiedAICommandProcessor()

    def handle_voice_input(self, voice_input: str) -> Dict[str, Any]:
        """
        Handle voice input and return structured response

        Args:
            voice_input: The voice input text

        Returns:
            Dict: Structured response containing command details and result
        """
        command = self.processor.execute(voice_input)
        return {
            "success": command.status == ExecutionStatus.SUCCESS,
            "command": command.to_dict(),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    def get_command_history(self, limit: int = 10) -> Dict[str, Any]:
        """Get recent command history"""
        return {
            "history": self.processor.get_history(limit),
            "total_commands": len(self.processor.command_history)
        }

    def register_custom_handler(self, command_type: CommandType, handler: Callable) -> None:
        """Register a custom command handler"""
        self.processor.register_handler(command_type, handler)

    def clear_history(self) -> None:
        """Clear command history"""
        self.processor.clear_history()


# Module-level convenience functions
_default_handler = VoiceCommandHandler()


def handle_voice_command(voice_input: str) -> Dict[str, Any]:
    """
    Process a voice command using the default handler

    Args:
        voice_input: The voice input text

    Returns:
        Dict: Response containing command details and result
    """
    return _default_handler.handle_voice_input(voice_input)


def get_handler() -> VoiceCommandHandler:
    """Get the default voice command handler instance"""
    return _default_handler


if __name__ == "__main__":
    # Example usage
    handler = VoiceCommandHandler()

    # Test various command types
    test_commands = [
        "Generate a Python function to calculate factorial",
        "Review this code for bugs",
        "Create documentation for the API",
        "Write unit tests for the login module",
        "Debug the authentication error",
        "Refactor this nested loop structure",
        "What is the difference between lists and tuples?",
        "Help me with my code",
    ]

    print("Voice Command Handler - Test Suite")
    print("=" * 50)

    for test_input in test_commands:
        result = handler.handle_voice_input(test_input)
        print(f"\nInput: {test_input}")
        print(f"Type: {result['command']['command_type']}")
        print(f"Status: {result['command']['status']}")
        print(f"Result: {result['command']['result']}")

    print("\n" + "=" * 50)
    print("Command History:")
    history = handler.get_command_history(limit=5)
    print(f"Total Commands: {history['total_commands']}")
