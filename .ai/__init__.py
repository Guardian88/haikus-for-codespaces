"""
AI Systems Initialization Module

This module serves as the main entry point for all AI systems and unified commands.
It initializes and orchestrates:
- Language Models
- Code Analysis Systems
- Content Generation Engines
- Automation Frameworks
- Integration Managers
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AISystemType(Enum):
    """Enumeration of available AI system types."""
    CODE_ANALYSIS = "code_analysis"
    CONTENT_GENERATION = "content_generation"
    LANGUAGE_MODEL = "language_model"
    AUTOMATION = "automation"
    INTEGRATION = "integration"


@dataclass
class AISystemConfig:
    """Configuration for AI systems."""
    system_type: AISystemType
    enabled: bool = True
    priority: int = 0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class UnifiedCommand:
    """Base class for unified AI commands."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def execute(self, *args, **kwargs) -> Any:
        """Execute the command. Should be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement execute method")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"


class AISystemsManager:
    """
    Central manager for all AI systems.
    Handles initialization, orchestration, and lifecycle management.
    """

    def __init__(self):
        self.systems: Dict[str, Any] = {}
        self.commands: Dict[str, UnifiedCommand] = {}
        self.config: Dict[str, AISystemConfig] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._initialized = False

    def register_system(
        self,
        system_id: str,
        system_instance: Any,
        config: AISystemConfig
    ) -> None:
        """Register an AI system."""
        self.systems[system_id] = system_instance
        self.config[system_id] = config
        self.logger.info(f"Registered AI system: {system_id}")

    def register_command(
        self,
        command_id: str,
        command: UnifiedCommand
    ) -> None:
        """Register a unified command."""
        self.commands[command_id] = command
        self.logger.info(f"Registered unified command: {command_id}")

    def get_system(self, system_id: str) -> Optional[Any]:
        """Retrieve a registered AI system."""
        return self.systems.get(system_id)

    def get_command(self, command_id: str) -> Optional[UnifiedCommand]:
        """Retrieve a registered unified command."""
        return self.commands.get(command_id)

    def list_systems(self) -> List[str]:
        """List all registered system IDs."""
        return list(self.systems.keys())

    def list_commands(self) -> List[str]:
        """List all registered command IDs."""
        return list(self.commands.keys())

    async def execute_command(
        self,
        command_id: str,
        *args,
        **kwargs
    ) -> Any:
        """Execute a unified command."""
        command = self.get_command(command_id)
        if not command:
            raise ValueError(f"Command not found: {command_id}")
        
        self.logger.info(f"Executing command: {command_id}")
        return await command.execute(*args, **kwargs)

    def initialize(self) -> None:
        """Initialize all registered AI systems."""
        if self._initialized:
            self.logger.warning("AI Systems already initialized")
            return

        self.logger.info("Initializing AI Systems Manager")
        self.logger.info(f"Registered systems: {len(self.systems)}")
        self.logger.info(f"Registered commands: {len(self.commands)}")
        self._initialized = True
        self.logger.info("AI Systems Manager initialized successfully")

    def shutdown(self) -> None:
        """Gracefully shutdown all AI systems."""
        self.logger.info("Shutting down AI Systems Manager")
        self._initialized = False


# Global AI Systems Manager Instance
_ai_manager: Optional[AISystemsManager] = None


def get_ai_manager() -> AISystemsManager:
    """Get or create the global AI Systems Manager instance."""
    global _ai_manager
    if _ai_manager is None:
        _ai_manager = AISystemsManager()
    return _ai_manager


def initialize_ai_systems() -> AISystemsManager:
    """
    Initialize all AI systems and return the manager.
    This is the main entry point for AI system initialization.
    """
    manager = get_ai_manager()
    manager.initialize()
    logger.info("All AI systems initialized")
    return manager


def register_ai_system(
    system_id: str,
    system_instance: Any,
    system_type: AISystemType,
    enabled: bool = True,
    priority: int = 0
) -> None:
    """Register an AI system with the global manager."""
    manager = get_ai_manager()
    config = AISystemConfig(
        system_type=system_type,
        enabled=enabled,
        priority=priority
    )
    manager.register_system(system_id, system_instance, config)


def register_ai_command(command_id: str, command: UnifiedCommand) -> None:
    """Register a unified command with the global manager."""
    manager = get_ai_manager()
    manager.register_command(command_id, command)


# Public API
__all__ = [
    'AISystemType',
    'AISystemConfig',
    'UnifiedCommand',
    'AISystemsManager',
    'get_ai_manager',
    'initialize_ai_systems',
    'register_ai_system',
    'register_ai_command',
]

logger.info("AI module initialized - Main entry point ready")
