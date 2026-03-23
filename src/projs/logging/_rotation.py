"""
Part 3: Daily log rotation and error handling

Add these methods to the ProjectsLogger class.
"""

from pathlib import Path
from datetime import datetime
import shutil


def _get_rotated_path(self, filepath: Path) -> Path:
    """
    Get the rotated path for a log file.
    
    If today is 2026-03-21 and the original path is:
      ~/.projects/logs/projs.log
    
    This returns:
      ~/.projects/logs/projs.log.2026-03-20  (yesterday's)
    
    The "current" log is always named projs.log (no date suffix).
    When a new day starts, the old one gets a date suffix and a new one starts.
    
    Args:
        filepath: The log file path (e.g., ~/.projects/logs/projs.log)
    
    Returns:
        Path with yesterday's date appended (e.g., ~/.projects/logs/projs.log.2026-03-20)
    """
    yesterday = (datetime.now() - __import__('datetime').timedelta(days=1)).strftime("%Y-%m-%d")
    return Path(str(filepath) + f".{yesterday}")


def _rotate_if_needed(self, filepath: Path) -> None:
    """
    Rotate log file if it's from a previous day.
    
    If the log file exists and is from yesterday (or earlier), rename it with
    the date suffix and let a new projs.log start.
    
    Example:
      - Old file: ~/.projects/logs/projs.log (created 2026-03-20)
      - Today is: 2026-03-21
      - Action: rename to ~/.projects/logs/projs.log.2026-03-20
      - Next write: creates fresh ~/.projects/logs/projs.log
    
    Args:
        filepath: The log file path
    """
    if not filepath.exists():
        return  # Nothing to rotate
    
    # Get the file's modification time
    mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    file_date = mtime.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # If the file is from before today, it needs rotation
    if file_date < today:
        rotated_path = self._get_rotated_path(filepath)
        try:
            shutil.move(str(filepath), str(rotated_path))
        except OSError as e:
            print(f"Warning: could not rotate {filepath}: {e}", file=sys.stderr)


def error_with_traceback(self, message: str, exception: Exception, 
                         project: str = None, global_event: bool = False) -> None:
    """
    Log an error with full traceback (for exceptions).
    
    Use this when catching an exception and want the full stack trace in the log.
    
    Args:
        message: High-level error message (e.g., "Project launch failed")
        exception: The exception object that was caught
        project: Optional project name
        global_event: If True, also write to global log
    
    Example:
        try:
            launcher.run()
        except Exception as e:
            logger.error_with_traceback("Project launch failed", e, 
                                       project="myproject", 
                                       global_event=False)
    """
    import traceback
    
    if not self._should_log("error"):
        return
    
    formatted = self._format_message("error", message)
    traceback_str = traceback.format_exc()
    full_message = formatted + "\n" + traceback_str
    
    # Write to user's local log
    try:
        filepath = self.user_log_root / "projs.log"
        self._rotate_if_needed(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'a') as f:
            f.write(full_message + '\n')
    except OSError as e:
        print(f"Warning: could not write error log: {e}", file=sys.stderr)
    
    # If it's a global event, also write to global log
    if global_event:
        try:
            filepath = self.global_log_dir / "projs.log"
            self._rotate_if_needed(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'a') as f:
                f.write(full_message + '\n')
        except OSError as e:
            print(f"Warning: could not write to global log: {e}", file=sys.stderr)
    
    # If it's project-specific, also write to project log
    if project:
        try:
            project_log_dir = self.project_logs_dir / project
            filepath = project_log_dir / "error.log"
            self._rotate_if_needed(filepath)
            project_log_dir.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'a') as f:
                f.write(full_message + '\n')
        except OSError as e:
            print(f"Warning: could not write to project log: {e}", file=sys.stderr)
