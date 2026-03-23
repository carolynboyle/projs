"""
Part 2: File writing and public logging methods

Add these methods to the ProjectsLogger class.
"""

import sys
from pathlib import Path


def _write_to_file(self, filepath: Path, message: str) -> None:
    """
    Write a message to a log file.
    
    Appends to the file (doesn't overwrite). Creates the file if it doesn't exist.
    
    Args:
        filepath: Where to write (e.g., ~/.projects/logs/projs.log)
        message: Formatted message (from _format_message)
    """
    try:
        # Make sure parent directories exist
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Append the message (mode='a' means append, not overwrite)
        with open(filepath, 'a') as f:
            f.write(message + '\n')
    except OSError as e:
        # If we can't write to the log file, print to stderr as fallback
        print(f"Warning: could not write to {filepath}: {e}", file=sys.stderr)


def debug(self, message: str, project: str = None) -> None:
    """
    Log a debug message (verbose, for troubleshooting).
    
    Args:
        message: What to log
        project: Optional project name (if this is a project-specific event)
    """
    if not self._should_log("debug"):
        return
    
    formatted = self._format_message("debug", message)
    
    # Always write to user's local log
    self._write_to_file(self.user_log_root / "projs.log", formatted)
    
    # If it's project-specific, also write to project log
    if project:
        project_log_dir = self.project_logs_dir / project
        self._write_to_file(project_log_dir / "debug.log", formatted)


def info(self, message: str, project: str = None, global_event: bool = False) -> None:
    """
    Log an info message (normal operation).
    
    Args:
        message: What to log
        project: Optional project name (if project-specific)
        global_event: If True, also write to global log
    """
    if not self._should_log("info"):
        return
    
    formatted = self._format_message("info", message)
    
    # Write to user's local log
    self._write_to_file(self.user_log_root / "projs.log", formatted)
    
    # If it's a global event, also write to global log
    if global_event:
        self._write_to_file(self.global_log_dir / "projs.log", formatted)
    
    # If it's project-specific, also write to project log
    if project:
        project_log_dir = self.project_logs_dir / project
        self._write_to_file(project_log_dir / "info.log", formatted)


def error(self, message: str, project: str = None, global_event: bool = False) -> None:
    """
    Log an error message (something went wrong).
    
    Args:
        message: What to log
        project: Optional project name (if project-specific)
        global_event: If True, also write to global log
    """
    if not self._should_log("error"):
        return
    
    formatted = self._format_message("error", message)
    
    # Write to user's local log
    self._write_to_file(self.user_log_root / "projs.log", formatted)
    
    # If it's a global event, also write to global log
    if global_event:
        self._write_to_file(self.global_log_dir / "projs.log", formatted)
    
    # If it's project-specific, also write to project log
    if project:
        project_log_dir = self.project_logs_dir / project
        self._write_to_file(project_log_dir / "error.log", formatted)
