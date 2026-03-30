# _foundation.py

**Path:** src/projs/logging/_foundation.py
**Syntax:** python
**Generated:** 2026-03-25 09:30:03

```python
"""
Part 1: Foundation - Logger class skeleton

This is the base structure. Part 2 adds the public methods.
"""

from pathlib import Path
from datetime import datetime
import sys


class ProjectsLogger:
    """Logs app and project events to master and per-project logs."""

    def __init__(self, config_manager):
        """
        Initialize logger.
        
        Args:
            config_manager: ConfigManager instance (gives us paths and settings)
        """
        self.config = config_manager
        self.user_log_root = self.config.root / "logs"
        
        # Global log location (fallback: use package location)
        # TODO: read app_root from system.yaml when installed
        self.global_log_dir = Path(__file__).parent.parent.parent / "logs"
        
        self.project_logs_dir = self.user_log_root / "projects"
        
        # Create directories if they don't exist
        self.user_log_root.mkdir(parents=True, exist_ok=True)
        self.project_logs_dir.mkdir(parents=True, exist_ok=True)
        self.global_log_dir.mkdir(parents=True, exist_ok=True)
        
        # Get log level from config (default to 'info')
        self.level = self.config.system.get("logging", {}).get("level", "info").lower()

    def _should_log(self, level: str) -> bool:
        """
        Check if a message at this level should be logged.
        
        Returns True if the message level is important enough to log.
        
        The hierarchy:
          debug (0) = tell me everything, I'm troubleshooting
          info (1)  = tell me what happened, normal operation
          error (2) = only tell me when something broke
        
        If system is set to 'info' (1), then:
          debug (0) → 0 >= 1? No, don't log
          info (1)  → 1 >= 1? Yes, log
          error (2) → 2 >= 1? Yes, log
        """
        levels = {"debug": 0, "info": 1, "error": 2}
        return levels.get(level, 1) >= levels.get(self.level, 1)

    def _format_message(self, level: str, message: str) -> str:
        """
        Format a log message with timestamp and level.
        
        Args:
            level: "debug", "info", or "error"
            message: The message content
        
        Returns:
            Formatted string like: "2026-03-21 14:32:10 | INFO     | Project created"
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"{timestamp} | {level.upper():8} | {message}"

```
