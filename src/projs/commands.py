"""
projs.commands - Command library management
"""

import json
from typing import Optional, List, Dict, Any

from projs.config import ConfigManager


class CommandLibrary:
    """Manages the command library."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.commands = self._load_commands()
    
    def _load_commands(self) -> Dict[str, Any]:
        """Load commands from commands.json."""
        if not self.config.commands_file.exists():
            return self._default_commands()
        
        return json.loads(self.config.commands_file.read_text())
    
    def _default_commands(self) -> Dict[str, Any]:
        """Default commands if file doesn't exist."""
        return {
            "commands": [
                {
                    # Single entry handles both cases:
                    #   .venv absent → create then activate
                    #   .venv present → activate only (never clobbers installed packages)
                    "id": "venv",
                    "name": "Create/activate venv",
                    "create_command": "python3 -m venv .venv && source .venv/bin/activate",
                    "activate_command": "source .venv/bin/activate",
                    "venv_path": ".venv",
                },
                {
                    "id": "git_init",
                    "name": "Initialize git",
                    "command": "git init",
                    # .git already present means repo is initialised — skip silently.
                    "idempotent_check": ".git",
                },
                {
                    "id": "git_commit",
                    "name": "Initial commit",
                    "command": 'git add . && git commit -m "Initial project scaffold"',
                    "requires_path": ".git",
                },
                {
                    "id": "codium",
                    "name": "Launch Codium",
                    "command": "codium .",
                },
                {
                    "id": "pytest",
                    "name": "Run pytest",
                    "command": "pytest",
                },
            ]
        }
    
    def get_all(self) -> List[Dict[str, str]]:
        """Get all available commands."""
        return self.commands.get("commands", [])
    
    def get_by_id(self, cmd_id: str) -> Optional[Dict[str, str]]:
        """Get a command by ID."""
        for cmd in self.get_all():
            if cmd["id"] == cmd_id:
                return cmd
        return None
