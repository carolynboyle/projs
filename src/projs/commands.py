"""
projs.commands - Command library management
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from projs.config import ConfigManager

_DATA_DIR = Path(__file__).parent / "data"


class CommandLibrary:
    """Manages the command library."""

    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.commands = self._load_commands()

    def _load_commands(self) -> Dict[str, Any]:
        """
        Load commands from commands.json.

        Tries user path (~/.projects/commands.json) first,
        falls back to shipped defaults in projs/data/commands.json.
        """
        for path in (
            self.config.commands_file,
            _DATA_DIR / "commands.json",
        ):
            if path.exists():
                try:
                    data = json.loads(path.read_text())
                    if data:
                        return data
                except Exception as e:
                    print(f"Warning: could not load {path}: {e}")

        print("Warning: no commands.json found, command library is empty.")
        return {"commands": []}

    def get_all(self) -> List[Dict[str, str]]:
        """Get all available commands."""
        return self.commands.get("commands", [])

    def get_by_id(self, cmd_id: str) -> Optional[Dict[str, str]]:
        """Get a command by ID."""
        for cmd in self.get_all():
            if cmd["id"] == cmd_id:
                return cmd
        return None
